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
    logging.info(f"Analyzing {filepath} with BirdNET Python API...")
    detections = []

    if model is None:
        logging.warning("BirdNET not loaded. Using mock analysis data.")
        detections.append({"species": "Columba palumbus", "confidence": 0.85})
        if filepath.exists():
            filepath.unlink()
        return detections

    try:
        # Get predictions directly from memory
        predictions = model.predict(str(filepath))

        # predictions is typically a pandas DataFrame
        if predictions is not None and not predictions.empty:
            for row in predictions.to_dict("records"):
                species = row.get("species_name", row.get("common_name", None))
                conf = row.get("confidence", 0.0)

                if species and float(conf) >= CONFIDENCE_THRESHOLD:
                    detections.append(
                        {"species": str(species), "confidence": float(conf)}
                    )

    except Exception as e:
        logging.error(f"BirdNET analyzer error: {e}")
    finally:
        if filepath.exists():
            filepath.unlink()  # Cleanup recorded audio segment

    return detections
