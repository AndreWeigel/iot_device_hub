import asyncio

from app.services.device_service import DeviceService
from app.db.session import db_session_context
from app.mqtt.mqtt_client import MQTTClient

mqtt_client = None  # Keep reference for shutdown

async def initialize_all_mqtt_subscriptions(loop):
    global mqtt_client
    mqtt_client = MQTTClient(client_id="myClient", loop=loop)

    async with db_session_context() as db:
        mqtt_topics = await DeviceService.get_mqtt_enabled_topics(db=db)

    mqtt_client.subscribe_to_topics(mqtt_topics)
    mqtt_client.connect()


async def initialize_single_mqtt_subscription(device_id):
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = MQTTClient(client_id="myClient", loop=asyncio.get_running_loop())
        mqtt_client.connect()

    async with db_session_context() as db:
        topic = await DeviceService.get_mqtt_topic_for_device(db=db, device_id=device_id)

    if topic:
        mqtt_client.subscribe_to_topics([topic])



async def disconnect_all_mqtt_subscriptions():
    if mqtt_client:
        mqtt_client.disconnect()
