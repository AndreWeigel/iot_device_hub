from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext



class UserService:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data):
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            new_user = User(
                email=data.email,
                username=data.username,
                hashed_password=pwd_context.hash(data.password)
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return True, new_user

        except SQLAlchemyError as e:
            self.db.rollback()
            return False, str(e)

    def get(self, user_search, by='id'):
        try:
            query = {
                'id': lambda val: self.db.query(User).get(val),
                'email': lambda val: self.db.query(User).filter_by(email=val).first(),
                'username': lambda val: self.db.query(User).filter_by(username=val).first()
            }

            user = query.get(by, query['id'])(user_search)
            return True, user
        except SQLAlchemyError as e:
            return False, str(e)


    def update(self, user_id, data):
        success, user = self.get(user_id)
        if not success or not user:
            return False, "User not found"
        try:
            update_data = data.dict(exclude_unset=True)

            # Prevent duplicate username or email
            if data.get('username') and data['username'] != user.username:
                existing = self.db.query(User).filter(User.username == data['username'], User.id != user.id).first()
                if existing:
                    return False, "Username already taken"

            if data.get('email') and data['email'] != user.email:
                existing = self.db.query(User).filter(User.email == data['email'], User.id != user.id).first()
                if existing:
                    return False, "Email already taken"

            if "username" in update_data:
                if self.get(update_data['username'], by = 'username'):
                    return False, "Username already taken"
                user.username = update_data["username"]

            if "email" in update_data:
                if self.get(update_data['email'], by = 'email'):
                    return False, "Email already taken"
                user.email = update_data["email"]

            if "password" in update_data:
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                user.hashed_password = pwd_context.hash(update_data["password"])

            self.db.commit()
            self.db.refresh(user)
            return True, user

        except SQLAlchemyError as e:
            return False, str(e)

    def delete(self, user_id):
        success, user = self.get(user_id)
        if not success or not user:
            return False, "User not found"
        try:
            self.db.delete(user)
            self.db.commit()
            return True, None
        except SQLAlchemyError as e:
            return False, str(e)