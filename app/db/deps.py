from app.db.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

