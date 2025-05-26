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

    def get_all(self):
        try:
            users = self.db.query(User).all()
            return True, users
        except SQLAlchemyError as e:
            return False, str(e)

    def update(self, user_id, data):
        user = self.db.query.get(user_id)
        if not user:
            return None
        try:
            user.username = data.get('username', user.username)

        except SQLAlchemyError as e:
            return False, str(e)













if __name__ == "__main__":
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Sample user data
    sample_data = {
        'username': 'andre',
        'email': 'andre@gmail.com',
        'hashed_password': pwd_context.hash("lol"),
        'status': True, }

    user_service = UserService(session)

    user = user_service.create(sample_data)



    # Example: Add a user
    # new_user = User(username="Andre", email="andr@example.com")
    # session.add(new_user)
    # session.commit()
    # session.close()