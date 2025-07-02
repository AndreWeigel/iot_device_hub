from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import create_db_and_tables
from app.mqtt.mqtt_service import initialize_all_mqtt_subscriptions, disconnect_all_mqtt_subscriptions
import asyncio

mqtt_loop = None  # Global event loop to pass into MQTT client

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_loop
    mqtt_loop = asyncio.get_running_loop()  # ✅ Set this once in main thread

    await create_db_and_tables()
    await initialize_all_mqtt_subscriptions(mqtt_loop)  # ✅ Pass the loop

    yield  # App runs

    await disconnect_all_mqtt_subscriptions()
