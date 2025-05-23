from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

class UserService:

    def __init__(self, db: Session):
        self.db = db


    def create(self, data):
        try:
            new_user = User(
                email=data['email'],
                username=data['username']
            )

            # add token generation here?

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return True, User

        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)




if __name__ == "__main__":

    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy import create_engine
    from sqlalchemy.exc import SQLAlchemyError
    from app.db.base import Base

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker, declarative_base

    from dotenv import load_dotenv
    import os

    load_dotenv()

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    # Set up SQLAlchemy ORM
    DATABASE_URL = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(DATABASE_URL, echo=True)

    Base.metadata.create_all(bind=engine)

    # Sample user data
    sample_data = {
        "email": "test@example.com",
        "username": "testuser"
    }

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    user_service = UserService(session)

    user = user_service.create(sample_data)

    # Example: Add a user
    # new_user = User(username="Andre", email="andr@example.com")
    # session.add(new_user)
    # session.commit()
    # session.close()