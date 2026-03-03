import birdnet
import logging

from src.worker.config import CONFIDENCE_THRESHOLD
from pathlib import Path


model = birdnet.load("acoustic", "2.4", "tf")


def analyze_audio(filepath: Path) -> list:
    """
    Uses the BirdNET Python API to process the generated audio snippet.
    Returns a list of dictionaries with species and confidence scores.
    """
    logging.info(f"Analysing {filepath} with BirdNET Python API...")
    detections = []

    try:
        # Get predictions directly from memory
        predictions = model.predict(str(filepath)).to_structured_array()

        # predictions is typically a pandas DataFrame
        if predictions is not None and len(predictions) > 0:
            for row in predictions:
                input_file = row[0]
                species = row[3]
                conf = row[4]

                if species and float(conf) >= CONFIDENCE_THRESHOLD:
                    detections.append(
                        {"species": str(species), "confidence": float(conf)}
                    )

        logging.info(f"Predictions: {predictions}")

    except Exception as e:
        logging.error(f"BirdNET analyzer error: {e}")
    finally:
        if filepath.exists():
            filepath.unlink()  # Cleanup recorded audio segment

    return detections
