from datetime import datetime
import asyncio
import httpx
import random
from fake_devices.config import BACKEND_URL, SEND_INTERVAL_SECONDS, DEVICES, LOGIN_URL
from app.models.device_data import DeviceDataIn


class DeviceSimulator:
    """
    Simulates a single IoT device that sends telemetry data to the backend
    at regular time intervals using HTTP POST requests.
    """
    def __init__(self, device_id: int, device_key: str, reading_type: str = "temperature", interval: int = SEND_INTERVAL_SECONDS):
        """Initialize a simulated device."""
        self.device_id = device_id
        self.device_key = device_key
        self.reading_type = reading_type
        self.interval = interval
        self.token = None

    async def login(self):
        """
        Authenticate using device credentials and store the JWT token.
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(LOGIN_URL, data={
                    "device_id": self.device_id,
                    "device_key": self.device_key
                })
                if response.status_code == 200:
                    self.token = response.json()["access_token"]
                    print(f"[Device {self.device_id}] Authenticated")
                else:
                    print(f"[Device {self.device_id}] Login failed: {response.text}")
            except Exception as e:
                print(f"[Device {self.device_id}] Login error: {e}")

    def _generate_payload(self) -> dict:
        """Generate a telemetry payload using the Pydantic schema."""
        data = DeviceDataIn(
            reading_type=self.reading_type,
            value=round(random.uniform(20.0, 30.0), 2),
            timestamp=datetime.utcnow()
        )
        return data.model_dump(mode="json")

    async def run(self):
        """
        Main loop: Authenticate and then continuously send telemetry data at regular intervals using asynchronous HTTP POST.
        Includes error handling and logs each request's result.
        """

        await self.login()

        if not self.token:
            print(f"[Device {self.device_id}] Skipping: No token.")
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        while True:
            payload = self._generate_payload()
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{BACKEND_URL}/devices/data",
                        json=payload,
                        headers=headers
                    )
                    print(f"[Device {self.device_id}] Sent: {payload} | Status: {response.status_code}")
            except Exception as e:
                print(f"[Device {self.device_id}] Error: {e}")

            await asyncio.sleep(self.interval)


async def run_multiple_simulators(devices: list[dict]):
    """Launch and run multiple DeviceSimulators concurrently using asyncio."""
    # Create an empty list to store simulator objects
    simulators = []

    # Create a DeviceSimulator for each device ID and add it to the list
    for device in devices:
        simulator = DeviceSimulator(device_id=device['ID'],device_key=device['KEY'])
        simulators.append(simulator)

    # Create an empty list to store coroutine tasks
    tasks = []

    # Prepare the coroutine for each simulator's run() method
    for simulator in simulators:
        task = simulator.run()  # This returns a coroutine (not running yet)
        tasks.append(task)

    # Use asyncio to run all coroutines concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run_multiple_simulators(DEVICES))


