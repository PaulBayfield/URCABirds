import birdnet
import logging

from src.worker.config import CONFIDENCE_THRESHOLD
from pathlib import Path


class Analyser:
    """
    Analyser class for handling audio analysis.
    """

    def __init__(self, model: str = "acoustic", version: str = "2.4", backend: str = "tf") -> None:
        """
        Initialises the Analyser with the provided model, version, and backend.

        :param model: The model to use for analysis.
        :type model: str
        :param version: The version of the model to use.
        :type version: str
        :param backend: The backend to use for analysis.
        :type backend: str
        """
        self.model = birdnet.load(model, version, backend)

    def analyse_audio(self, filepath: Path) -> list:
        """
        Uses the BirdNET Python API to process the generated audio snippet.
        Returns a list of dictionaries with species and confidence scores.

        :param filepath: The path to the audio file to analyse.
        :type filepath: Path
        :return: A list of dictionaries with species and confidence scores.
        :rtype: list
        """
        logging.info(f"Analysing {filepath} with BirdNET Python API...")
        detections = []

        try:
            # Get predictions directly from memory
            predictions = self.model.predict(str(filepath)).to_structured_array()

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
