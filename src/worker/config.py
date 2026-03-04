import os


API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
SENSOR_ID = os.getenv("SENSOR_ID")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD"))

LATITUDE = float(os.getenv("LATITUDE"))
LONGITUDE = float(os.getenv("LONGITUDE"))

AUDIO_DURATION = 10  # Length of captured audio segment in seconds
DB_PATH = "cache.db"
LOG_PATH = "worker.log"
