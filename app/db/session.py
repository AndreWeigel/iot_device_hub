import os
from dotenv import load_dotenv

from contextlib import asynccontextmanager
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

# Get full database URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable is not set.")

# Create an async SQLAlchemy engine instance
engine = create_async_engine(DATABASE_URL,
                             echo=False, # Set to True for verbose SQL output during development
                             future = True
                             )

# Create a session factory bound to the async engine
# expire_on_commit=False means objects remain usable after committing
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def create_db_and_tables():
    """
    Creates all tables in the database based on SQLModel metadata.
    Use this during application startup or initial setup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def reset_db():
    """
    Drops the entire public schema and recreates it, including all tables.

    WARNING: This is destructive and should only be used in development/testing.
    """
    async with engine.begin() as conn:
        # Drop the schema and recreate it in two separate calls
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        # Now recreate all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def _get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Core async generator that creates and yields an SQLAlchemy AsyncSession.

    Used internally to support both FastAPI dependency injection and
    context-managed usage in scripts/tests."""
    async with async_session() as session:
        yield session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI-compatible dependency for providing a database session.
    Automatically manages session lifecycle per request.
        """
    async for session in _get_session():
        yield session

@asynccontextmanager
async def db_session_context():
    """
    Async context manager version of the database session for use in scripts,
    background tasks, or tests.
    """
    async for session in _get_session():
        yield session


# Running this script will delete all current tables and recreate them
if __name__ == "__main__":

    import asyncio
    asyncio.run(reset_db())