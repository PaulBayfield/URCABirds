import asyncio
import logging
import time
import os
import concurrent.futures

from config import (
    LOG_PATH,
    SENSOR_ID,
    SENSOR_NAME,
    API_URL,
    API_KEY,
    LATITUDE,
    LONGITUDE,
)
from utils.db import Database
from utils.audio import Audio
from utils.analyser import Analyser
from utils.api import APIClient
from datetime import datetime, timezone
from pathlib import Path
from aiohttp import ClientSession


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)


class Worker:
    """
    Worker class for processing audio segments and sending detections to the API.
    """

    def __init__(self, session: ClientSession) -> None:
        """
        Initialise the worker with a session.

        :param session: The session to use for API requests.
        :type session: ClientSession
        """
        self.session = session

        self.database = Database()
        self.database.init()

        self.analyser = Analyser()

        self.api_client = APIClient(self.session, API_URL, API_KEY, SENSOR_ID)

        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max(1, (os.cpu_count() or 2) - 1)
        )

    async def sync_offline_data(self) -> None:
        """
        Scans local SQLite database for entries not yet sent to the API.
        """
        unsynced_records = self.database.get_unsynced_records()

        if unsynced_records:
            logging.info(f"Attempting to sync {len(unsynced_records)} offline records.")

        for record in unsynced_records:
            success = await self.api_client.send_detection(
                record, self.database, record_id=record["id"]
            )

            if not success:
                break

    async def process_audio_segment(
        self,
        filepath: Path,
        timestamp: str,
    ) -> None:
        """
        Process an audio segment.

        :param filepath: The path to the audio file.
        :type filepath: Path
        :param timestamp: The timestamp of the audio segment.
        :type timestamp: str
        """
        try:
            # 2. Analyze the segment
            loop = asyncio.get_running_loop()
            detections = await loop.run_in_executor(
                self.executor, self.analyser.analyse_audio, filepath
            )

            if detections:
                print(detections)

            # 3. Handle detections
            for det in detections:
                det["timestamp"] = timestamp
                logging.info(
                    f"BIRD DETECTED: {det['species']} with {det['confidence']:.2f} confidence."
                )

                # Attempt to push to API immediately
                success = await self.api_client.send_detection(det, self.database)

                if not success:
                    # Stash offline
                    self.database.cache_detection(
                        timestamp, det["species"], det["confidence"]
                    )
        except Exception as e:
            logging.error(f"Unexpected fault in processing segment: {e}", exc_info=True)

    async def run(self):
        logging.info(f"URCABirds Worker Node [{SENSOR_ID}] initializing...")

        # Self-register / update last_connection on startup
        await self.api_client.register_sensor(
            name=SENSOR_NAME,
            latitude=LATITUDE,
            longitude=LONGITUDE,
        )

        while True:
            try:
                # 1. Start audio segment capture with unique timestamp in a thread to avoid blocking loop
                now_ts = datetime.now(timezone.utc).isoformat()
                safe_ts = now_ts.replace(":", "-").replace(".", "-").replace("+", "-")
                temp_audio_file = Path(f"./captures/capture_{safe_ts}.wav")

                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    self.executor, Audio().record, temp_audio_file
                )

                # 2. Analyze the segment asynchronously
                asyncio.create_task(self.process_audio_segment(temp_audio_file, now_ts))

                # 4. Periodically try and flush offline detections
                await self.sync_offline_data()

            except KeyboardInterrupt:
                logging.info("Worker Node stopped gracefully by user.")
                await self.close()
                break
            except Exception as e:
                logging.error(f"Unexpected fault in detection loop: {e}", exc_info=True)
                # Short cooldown to avoid aggressive error looping
                time.sleep(5)

    async def close(self) -> None:
        """
        Closes the worker and its resources.
        """
        self.executor.shutdown(wait=True)
        await self.database.close()
