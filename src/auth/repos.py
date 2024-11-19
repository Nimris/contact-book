from sqlalchemy import select

from src.auth.pass_utilits import get_password_hash
from src.auth.shema import UserCreate
from src.auth.models import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def create_user(self, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
    
    
    async def get_user_by_email(self, email):
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    
    async def get_user_by_username(self, username):
        result = await self.session.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()