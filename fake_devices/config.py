import os
from dotenv import load_dotenv
import json

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SEND_INTERVAL_SECONDS = 5

dict_str = os.getenv("DEVICES")
DEVICES = json.loads(dict_str)
LOGIN_URL = f"{BACKEND_URL}/device/token"
