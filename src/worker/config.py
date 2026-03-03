import os


# ---------- Configuration ----------
API_URL = os.getenv("API_URL", "https://api.urcabirds.local/v1")
API_KEY = os.getenv("API_KEY", "default-api-key")
SENSOR_ID = os.getenv("SENSOR_ID", "rpi-moulin-01")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))

LATITUDE = float(os.getenv("LATITUDE", "49.24"))  # Reims, Campus Moulin de la Housse
LONGITUDE = float(os.getenv("LONGITUDE", "4.06"))

AUDIO_DURATION = 10  # Length of captured audio segment in seconds
DB_PATH = "cache.db"
LOG_PATH = "worker.log"
