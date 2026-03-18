import os

from dotenv import load_dotenv


load_dotenv()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"


API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
SENSOR_ID = os.getenv("SENSOR_ID")
SENSOR_NAME = os.getenv("SENSOR_NAME", SENSOR_ID)
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD"))

LATITUDE = float(os.getenv("LATITUDE"))
LONGITUDE = float(os.getenv("LONGITUDE"))

AUDIO_DURATION = 10  # Length of captured audio segment in seconds
DB_PATH = "cache.db"
