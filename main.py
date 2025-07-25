from fastapi import FastAPI
from app.routes import device
from app.routes import user, device_data
from app.lifespan import lifespan

# Create the FastAPI app instance
app = FastAPI(
    title="IOT HUB API",
    description="""
    An IoT Hub API to manage users and registered IoT devices, 
    and to ingest, store, and retrieve telemetry data sent from those devices. 
    Supports user authentication, device provisioning, and real-time data ingestion.
    """,
    version="1.0.0",
    docs_url="/",
    lifespan = lifespan
)

# Include user-related routes
app.include_router(user.router)

# Include device-related routes
app.include_router(device.router)

# Include device data-related routes
app.include_router(device_data.router)
