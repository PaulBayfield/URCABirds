import asyncio
import logging
import time
import os
import concurrent.futures


from src.worker.config import LOG_PATH, SENSOR_ID, API_URL, API_KEY
from src.worker.utils.db import init_db, cache_detection, get_unsynced_records
from src.worker.utils.audio import record_audio
from src.worker.utils.analyzer import analyze_audio
from src.worker.utils.api import APIClient
from datetime import datetime, timezone
from pathlib import Path
from aiohttp import ClientSession

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)


async def sync_offline_data(api_client: APIClient):
    """Scans local SQLite database for entries not yet sent to the API."""
    unsynced_records = get_unsynced_records()

    if unsynced_records:
        logging.info(f"Attempting to sync {len(unsynced_records)} offline records.")

    for record in unsynced_records:
        success = await api_client.send_detection(record, record_id=record["id"])
        if not success:
            # Quit early since network is still struggling
            break


async def process_audio_segment(
    filepath: Path, timestamp: str, api_client: APIClient, executor
):
    try:
        # 2. Analyze the segment
        loop = asyncio.get_running_loop()
        detections = await loop.run_in_executor(executor, analyze_audio, filepath)

        if detections:
            print(detections)

        # 3. Handle detections
        for det in detections:
            det["timestamp"] = timestamp
            logging.info(
                f"BIRD DETECTED: {det['species']} with {det['confidence']:.2f} confidence."
            )

            # Attempt to push to API immediately
            success = await api_client.send_detection(det)

            if not success:
                # Stash offline
                cache_detection(timestamp, det["species"], det["confidence"])
    except Exception as e:
        logging.error(f"Unexpected fault in processing segment: {e}", exc_info=True)


# ---------- Main Execution Loop ----------
async def main():
    print("Main thread")

    logging.info(f"URCABirds Worker Node [{SENSOR_ID}] initializing...")
    init_db()

    session = ClientSession()
    api_client = APIClient(session, API_URL, API_KEY, SENSOR_ID)

    # Use multiple worker threads to process detections in parallel and prevent bottlenecking
    max_threads = max(1, (os.cpu_count() or 2) - 1)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)

    while True:
        try:
            # 1. Start audio segment capture with unique timestamp in a thread to avoid blocking loop
            now_ts = datetime.now(timezone.utc).isoformat()
            safe_ts = now_ts.replace(":", "-").replace(".", "-").replace("+", "-")
            temp_audio_file = Path(f"capture_{safe_ts}.wav")

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(executor, record_audio, temp_audio_file)

            # 2. Analyze the segment asynchronously
            asyncio.create_task(
                process_audio_segment(temp_audio_file, now_ts, api_client, executor)
            )

            # 4. Periodically try and flush offline detections
            await sync_offline_data(api_client)

        except KeyboardInterrupt:
            logging.info("Worker Node stopped gracefully by user.")
            executor.shutdown(wait=True)
            await session.close()
            break
        except Exception as e:
            logging.error(f"Unexpected fault in detection loop: {e}", exc_info=True)
            # Short cooldown to avoid aggressive error looping
            time.sleep(5)
