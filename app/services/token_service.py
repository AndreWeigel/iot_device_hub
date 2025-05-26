from uuid import uuid4
import bcrypt

from app.models.api_token import APIToken
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

class TokenService:

    def __init__(self, db: Session):
        self.db = db


    def generate_api_token_for_user_id(self, user_id: int):
        try:
            raw_token = str(uuid4())
            hashed_token = bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()

            new_api_token = APIToken(
                token_hash=hashed_token,
                user_id=user_id
            )
            self.db.add(new_api_token)
            self.db.commit()
            self.db.refresh(new_api_token)

            # Return the raw token for the user to store; hash is stored in DB
            return True, raw_token
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)