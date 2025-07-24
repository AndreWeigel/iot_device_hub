import asyncio
import os

from app.services.device_service import DeviceService
from app.db.session import db_session_context
from app.mqtt.mqtt_client import MQTTClient

from sqlalchemy import select
from dotenv import load_dotenv
load_dotenv()

mqtt_client = None  # Keep reference for shutdown


def get_broker_url():
    return os.getenv("MQTT_BROKER_URL", "localhost")


async def initialize_all_mqtt_subscriptions(loop):

    global mqtt_client
    broker_url = get_broker_url()
    mqtt_client = MQTTClient(client_id="myClient", loop=loop, broker=broker_url)

    try:
        async with db_session_context() as db:
            mqtt_topics = await DeviceService.get_mqtt_enabled_topics(db=db)

        mqtt_client.subscribe_to_topics(mqtt_topics)
        mqtt_client.connect()
    except ConnectionRefusedError as e:
        print(f"🚫 MQTT connection failed: {e}")
    except Exception as e:
        print(f"Unexpected error during MQTT setup: {e}")


async def initialize_single_mqtt_subscription(device_id):
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = MQTTClient(client_id="myClient", loop=asyncio.get_running_loop())
        try:
            mqtt_client.connect()
        except Exception as e:
            print(f"Failed to connect MQTT client: {e}")
            return

    try:
        async with db_session_context() as db:
            topic = await DeviceService.get_mqtt_topic_for_device(db=db, device_id=device_id)

        if topic:
            mqtt_client.subscribe_to_topics([topic])
    except Exception as e:
        print(f"Failed to subscribe device {device_id} to MQTT: {e}")



async def disconnect_all_mqtt_subscriptions():
    if mqtt_client:
        mqtt_client.disconnect()
