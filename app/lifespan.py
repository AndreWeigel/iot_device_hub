from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    #  Startup logic
    await create_db_and_tables()

    # The app runs normally
    yield