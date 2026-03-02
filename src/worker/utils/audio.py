import logging
import time
import sounddevice as sd
import soundfile as sf

from src.worker.config import AUDIO_DURATION
from pathlib import Path


def record_audio(filepath: Path):
    """
    Captures audio for the configured duration. Uses sounddevice and soundfile.
    Fallback to a mock method during local testing off-device.
    """
    logging.info(f"Recording audio segment to {filepath}...")
    try:
        # cd format is typically 44100 Hz, 16-bit, stereo
        fs = 44100
        channels = 2
        # Record audio
        recording = sd.rec(
            int(AUDIO_DURATION * fs), samplerate=fs, channels=channels, dtype="int16"
        )
        sd.wait()  # Wait until recording is finished
        sf.write(str(filepath), recording, fs, subtype="PCM_16")
    except Exception as e:
        logging.warning("Audio capture failed, employing mock recording.")
        logging.error(f"Error recording audio: {e}")
        time.sleep(AUDIO_DURATION)
        # Touch mock file
        with open(filepath, "wb") as f:
            f.write(b"mock audio data")
