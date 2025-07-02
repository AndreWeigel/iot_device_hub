import asyncio
import httpx
import random
from fake_devices.config import BACKEND_URL, SEND_INTERVAL_SECONDS, DEVICES, LOGIN_URL
from app.models.device_data import DeviceDataIn
from app.utils import now_utc
import json
import paho.mqtt.client as mqtt



# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_TEMPLATE = "devices/{device_id}"


class DeviceSimulator:
    """
    Simulates an IoT device sending telemetry data via HTTP or MQTT.
    """

    def __init__(
        self,
        device_id: int,
        device_key: str,
        reading_type: str = "temperature",
        interval: int = SEND_INTERVAL_SECONDS,
        protocol: str = "http",  # "http" or "mqtt"
    ):
        self.device_id = device_id
        self.device_key = device_key
        self.reading_type = reading_type
        self.interval = interval
        self.protocol = protocol
        self.token = None
        self.mqtt_client = None

    async def login(self):
        """Authenticate device and store JWT token."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    LOGIN_URL,
                    data={"device_id": self.device_id, "device_key": self.device_key},
                )
                if response.status_code == 200:
                    self.token = response.json()["access_token"]
                    print(f"[Device {self.device_id}] Authenticated")
                else:
                    print(f"[Device {self.device_id}] Login failed: {response.text}")
            except Exception as e:
                print(f"[Device {self.device_id}] Login error: {e}")

    def _generate_payload(self) -> dict:
        """Generate telemetry payload."""
        data = DeviceDataIn(
            reading_type=self.reading_type,
            value=round(random.uniform(20.0, 30.0), 2),
            timestamp=now_utc(),
        )
        return data.model_dump(mode="json")

    def _setup_mqtt(self):
        """Setup MQTT client."""
        self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.mqtt_client.loop_start()

    def _send_mqtt(self, payload: dict):
        """Send payload via MQTT."""
        topic = MQTT_TOPIC_TEMPLATE.format(device_id=self.device_id)
        mqtt_payload = json.dumps({
            "token": self.token,
            "data": payload
        })
        result = self.mqtt_client.publish(topic, mqtt_payload, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[Device {self.device_id}] ✅ MQTT sent to topic `{topic}`")
        else:
            print(f"[Device {self.device_id}] ❌ MQTT send failed")

    async def _send_http(self, payload: dict):
        """Send payload via HTTP POST."""
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/devices/data",
                    json=payload,
                    headers=headers,
                )
                print(f"[Device {self.device_id}] HTTP sent: {payload} | Status: {response.status_code}")
        except Exception as e:
            print(f"[Device {self.device_id}] HTTP error: {e}")

    async def run(self):
        """Main loop."""
        await self.login()

        if not self.token:
            print(f"[Device {self.device_id}] Skipping: No token.")
            return

        if self.protocol == "mqtt":
            self._setup_mqtt()

        try:
            while True:
                payload = self._generate_payload()
                if self.protocol == "http":
                    await self._send_http(payload)
                elif self.protocol == "mqtt":
                    self._send_mqtt(payload)
                await asyncio.sleep(self.interval)
        finally:
            if self.protocol == "mqtt":
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()


async def run_multiple_simulators(device_configs):
    """
    Launches multiple DeviceSimulator instances concurrently.

    Args:
        device_configs (list[dict]): List of configs with keys:
            - device_id (int)
            - device_key (str)
            - protocol (str): "http" or "mqtt"
            - reading_type (str, optional)
            - interval (int, optional)
    """
    simulators = [
        DeviceSimulator(
            device_id=cfg["device_id"],
            device_key=cfg["device_key"],
            protocol=cfg.get("protocol", "http"),
            reading_type=cfg.get("reading_type", "temperature"),
            interval=cfg.get("interval", 5),
        )
        for cfg in device_configs
    ]

    await asyncio.gather(*(sim.run() for sim in simulators))


if __name__ == "__main__":

    with open("device_list.json") as f:
        device_list = json.load(f)

    asyncio.run(run_multiple_simulators(device_list))
