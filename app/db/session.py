import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from typing import AsyncGenerator
from sqlmodel import SQLModel


# Import models so Alembic can detect them during autogeneration
from app.models.user import User
from app.models.device_data import DeviceData
from app.models.device import Device

# Load environment variables from a .env file into the process
load_dotenv()

# Read database connection parameters from the environment
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Compose the database connection URL for asyncpg and SQLAlchemy
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Ensure that all required variables are present
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL parameters not set in .env")

# Create an async SQLAlchemy engine instance
engine = create_async_engine(DATABASE_URL,
                             echo=False, # Set to True for verbose SQL output during development
                             future = True
                             )

# Create a session factory bound to the async engine
# expire_on_commit=False means objects remain usable after committing
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def reset_db():
    async with engine.begin() as conn:
        # Drop the schema and recreate it in two separate calls
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        # Now recreate all tables
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db_session() ->  AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields a SQLAlchemy AsyncSession.

    Yields an AsyncSession for use with FastAPI's dependency injection system.
    Automatically closes the session when the request is complete.
    """
    async with async_session() as session:
        yield session # The session is automatically closed when the request is done

if __name__ == "__main__":
    import asyncio
    asyncio.run(reset_db())