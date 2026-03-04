import logging
import time
import sounddevice as sd
import soundfile as sf

from src.worker.config import AUDIO_DURATION
from pathlib import Path


class Audio:
    """
    Audio class for recording audio segments.
    """

    def __init__(self) -> None:
        """
        Initialises the Audio class with the default values.
        """
        self.fs = 44100
        self.channels = 2

    def record(self, filepath: Path) -> None: 
        """
        Captures audio for the configured duration. Uses sounddevice and soundfile.
        Fallback to a mock method during local testing off-device.

        :param filepath: The path to the file to save the audio to.
        :type filepath: Path
        """
        logging.info(f"Recording audio segment to {filepath}...")

        try:
            recording = sd.rec(
                int(AUDIO_DURATION * self.fs), samplerate=self.fs, channels=self.channels, dtype="int16"
            )

            sd.wait()

            sf.write(str(filepath), recording, self.fs, subtype="PCM_16")
        except Exception as e:
            logging.warning("Audio capture failed, employing mock recording.")
            logging.error(f"Error recording audio: {e}")

            time.sleep(AUDIO_DURATION)

            with open(filepath, "wb") as f:
                f.write(b"mock audio data")
