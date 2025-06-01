from fastapi import FastAPI
from app.api.routes import user, device, device_data


# Create the FastAPI app instance
app = FastAPI(
    title="IOT HUB API",
    description="""
    An IoT Hub API to manage users and registered IoT devices, 
    and to ingest, store, and retrieve telemetry data sent from those devices. 
    Supports user authentication, device provisioning, and real-time data ingestion.
    """,
    version="1.0.0"
)

# Include user-related routes
app.include_router(user.router)

# Include device-related routes
app.include_router(device.router)

# Include device data-related routes
app.include_router(device_data.router)
