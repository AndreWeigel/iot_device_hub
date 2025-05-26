from app.db.session import SessionLocal
from sqlalchemy.orm import Session

# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

