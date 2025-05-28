from fastapi import FastAPI
from app.api.routes import user, device

app = FastAPI()

# Include routers
app.include_router(user.router)
app.include_router(device.router)
