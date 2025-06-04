import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SEND_INTERVAL_SECONDS = 5

DEVICE_ID = os.getenv("SENSOR_1_ID")
DEVICE_KEY = os.getenv("SENSOR_1_KEY")
LOGIN_URL = f"{BACKEND_URL}/device/token"
