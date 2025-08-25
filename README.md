<img src="streamlit_app/assets/logo.png" alt="IoT Device Hub Logo" width="100">

# IoT Device Hub

A backend service and lightweight dashboard for onboarding IoT devices, collecting their telemetry via **HTTP** and **MQTT**, and visualising the data in real‑time.

---

## 🚀 Features

* **User management** – JWT‑secured signup / login.
* **Device CRUD** – register, update, and remove devices that belong to a user.
* **Protocol bridge**  
  * REST endpoints for devices that speak HTTP  
  * MQTT subscription for low‑latency telemetry
* **Data persistence** – pluggable DB (PostgreSQL or SQLite by default).
* **Simulator** – spin up fake devices that publish over HTTP and/or MQTT.
* **Streamlit dashboard** – quick glance at the latest readings.

---

## 🗂️ Project layout

```text
.
├── app/               # FastAPI application (routers, models, services)
├── fake_devices/      # Device simulator classes
├── streamlit_app/     # Streamlit UI
├── tests/             # pytest suites
└──  main.py            # API entry‑point
```

---

## 🛠️ Getting started

### Prerequisites

* Python ≥ 3.9
* Running MQTT broker (e.g. Mosquitto)
* PostgreSQL § or SQLite
* `pip` for dependency management

### Installation

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Start the backend

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive OpenAPI UI.

### Start the dashboard

```bash
cd streamlit_app
streamlit run main.py
```

---

## 🔄 Simulating devices

When a new device is created, the system generates a `device_key`. This key must be used by the simulator to authenticate when sending data via HTTP or MQTT.

The simulator can run one or more devices using a JSON file like this:

```json
[
  {
    "device_id": 1,
    "device_key": "YOUR_DEVICE_KEY",
    "protocol": "http"
  },
  {
    "device_id": 1,
    "device_key": "YOUR_DEVICE_KEY",
    "protocol": "mqtt"
  }
]
```

Save it as `device_list.json`, then run the simulators:

```python
import asyncio
import json
from device_simulator.simulator import run_multiple_simulators

with open("device_list.json") as f:
    device_list = json.load(f)

asyncio.run(run_multiple_simulators(device_list))
```

You can launch multiple simulated devices in parallel to stress‑test the hub.

---

## 📡 MQTT quick‑start

Run Mosquitto in Docker:

```bash
docker run -it -p 1883:1883 eclipse-mosquitto
```

Update the broker URL/credentials in `app/core/config.py` before starting the API.

---

## 🧪 Testing

```bash
pytest
```

---

## 🗺️ Roadmap

- [ ] WebSocket push for live dashboard updates  
- [ ] Improved Streamlit UX (charts, auth)  
- [ ] Dockerfile + GitHub Actions CI  
- [ ] Terraform/Kubernetes deployment manifests  

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
