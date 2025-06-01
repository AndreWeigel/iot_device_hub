from typing import AsyncGenerator
from app.db.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession

# Dependency to get DB session
async def get_db() ->  AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields a SQLAlchemy AsyncSession.

    Yields an AsyncSession for use with FastAPI's dependency injection system.
    Automatically closes the session when the request is complete.
    """
    async with async_session() as session:
        yield session # The session is automatically closed when the request is done