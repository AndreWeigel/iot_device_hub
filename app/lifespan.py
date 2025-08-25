from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import create_db_and_tables
from app.mqtt.mqtt_service import initialize_all_mqtt_subscriptions, disconnect_all_mqtt_subscriptions
import asyncio
import os

mqtt_loop = None  # Global event loop to pass into MQTT client
DISABLE_MQTT = os.getenv("DISABLE_MQTT") == "1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_loop
    mqtt_loop = asyncio.get_running_loop()  # ✅ Set this once in main thread

    await create_db_and_tables()

    if not DISABLE_MQTT:
        await initialize_all_mqtt_subscriptions(mqtt_loop)
    yield
    if not DISABLE_MQTT:
        await disconnect_all_mqtt_subscriptions()

