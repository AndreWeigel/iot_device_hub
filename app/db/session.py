from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from dotenv import load_dotenv
import os

load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Set up SQLAlchemy ORM
DATABASE_URL = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()