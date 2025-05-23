from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone, timedelta
from app.db.base import Base

EXPIRATION_PERIOD_DAYS = 90

class APIToken(Base):

    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    status = Column(Boolean,  default = True, index=True, nullable=False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, default = lambda: datetime.now(timezone.utc) + timedelta(days=EXPIRATION_PERIOD_DAYS), nullable=True)
