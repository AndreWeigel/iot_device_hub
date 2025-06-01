import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Import the declarative base and model classes to ensure table definitions are registered
from app.db.base import Base
from app.models.user import User
from app.models.device_data import DeviceData
from app.models.device import Device

# Load environment variables from a .env file into the process
load_dotenv()

# Read database connection parameters from the environment
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Compose the database connection URL for asyncpg and SQLAlchemy
DATABASE_URL = f"postgresql+asyncpg://{db_user}@{db_host}:{db_port}/{db_name}"

# Ensure that all required variables are present
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL parameters not set in .env")

# Create an async SQLAlchemy engine instance
engine = create_async_engine(DATABASE_URL,
                             echo=False # Set to True for verbose SQL output during development
                             )

# Create a session factory bound to the async engine
# expire_on_commit=False means objects remain usable after committing
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
