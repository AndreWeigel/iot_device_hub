# mqtt_client.py
import paho.mqtt.client as mqtt
import json
from app.models.device_data import DeviceData
from app.models.device import Device  # assuming this exists
from app.auth.auth_device_handler import verify_device_token
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import asyncio
from app.utils import now_utc
from app.db.session import db_session_context
from sqlalchemy.exc import SQLAlchemyError


class MQTTClient:
    def __init__(self, client_id, broker="localhost", port=1883, keepalive=60, loop=None):
        """Initializes the MQTT client."""
        self.loop = loop or asyncio.get_event_loop()
        self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self.subscriptions = []

    def on_connect(self, client, userdata, flags, reasonCode, properties):
        """Callback function triggered upon a successful connection to the broker.
        Subscribes to any pre-defined topics in the subscription list."""
        print(f"[Connected] Reason code: {reasonCode}")
        for topic in self.subscriptions:
            print(f"[MQTT] Subscribing to topic: {topic}")
            self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        """Callback function triggered when a PUBLISH message is received."""
        print(f"[MQTT] Received on {msg.topic}: {msg.payload.decode()}")

        try:
            # Parse MQTT message payload
            payload = json.loads(msg.payload.decode())

            # Validate payload structure
            if "data" not in payload or "token" not in payload:
                print(f"[ERROR] Invalid payload structure: {payload}")
                return

            # Run coroutine safely from a thread
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._store_device_data(msg.topic, payload),
                    self.loop
                )
            else:
                print("[ERROR] No running event loop")

        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON from message: {msg.payload}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")

    def connect(self):
        """Connects to the MQTT broker and starts the network loop in a separate thread."""
        self.client.connect(self.broker, self.port, self.keepalive)
        self.client.loop_start()

    def subscribe_to_topics(self, topics):
        """Subscribes the client to a list of MQTT topics."""
        self.subscriptions.extend(topics)
        for topic in topics:
            self.client.subscribe(topic)

    def disconnect(self):
        """Stops the network loop and disconnects from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()

    @staticmethod
    async def _store_device_data(topic: str, payload: dict):
        """
        Stores device data from an MQTT message directly to the database.
        Assumes payload contains 'token' and 'data' keys.
        """
        # Extract fields
        token = payload.get("token")
        data = payload.get("data")

        device_id = int(topic.split("/")[-1])
        try:
            # Connect to DB
            async with db_session_context() as db:  # AsyncSession
                # Validate JWT
                is_authenticated = verify_device_token(token)
                if not is_authenticated:
                    raise ValueError("Device not authorized")

                try:
                    raw_timestamp = data.get("timestamp")
                    if isinstance(raw_timestamp, str):
                        # Convert ISO 8601 string to datetime object
                        timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
                    else:
                        timestamp = now_utc()
                    # Step 3: Create new DeviceData entry
                    db_data = DeviceData(
                        device_id=device_id,
                        reading_type=data.get("reading_type"),
                        value=data.get("value"),
                        timestamp=timestamp,
                    )

                    db.add(db_data)
                    await db.commit()
                    await db.refresh(db_data)
                except SQLAlchemyError as e:
                    await db.rollback()
                    print(e)

        except Exception as session_exc:
            print(f"[ERROR] Failed to get DB session: {session_exc}")
