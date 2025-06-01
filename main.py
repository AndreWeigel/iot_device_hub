from fastapi import FastAPI
from app.api.routes import user, device, device_data

app = FastAPI()

# Include routers
app.include_router(user.router)
app.include_router(device.router)

app.include_router(device_data.router)
