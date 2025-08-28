# app/main.py (or wherever this lives)
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routes import user, device, device_data
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
    docs_url="/docs",
    lifespan = lifespan
)

# CORS for local dev (Vite runs on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Group everything under /api ---
api = APIRouter(prefix="/api")
api.include_router(user.router, prefix="/users", tags=["users"])
api.include_router(device.router, prefix="/devices", tags=["devices"])
api.include_router(device_data.router, prefix="/device-data", tags=["device-data"])
app.include_router(api)


@app.get("/api/health")
def health():
    return {"ok": True}