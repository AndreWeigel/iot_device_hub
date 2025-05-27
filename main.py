from fastapi import FastAPI
from app.api.routes import user

app = FastAPI()

# Include routers
app.include_router(user.router)
