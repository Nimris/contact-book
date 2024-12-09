from fastapi import HTTPException
from sqlalchemy import select

from src.auth.pass_utilits import get_password_hash
from src.auth.shema import RoleEnum, UserCreate
from src.auth.models import Role, User


class UserRepository:
    def __init__(self, session, role_repo=None):
        self.session = session
        self.role_repo = role_repo or RoleRepository(session)
        
    async def update_avatar(self, email, url) -> User:
        """
        Updates user avatar
        
        :param email: User email
        :type email: str
        :param url: Avatar url
        :type url: str
        :return: Updated user object
        :rtype: User
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
        
        
    async def delete_user(self, email: str):
        """
        Deletes user by email
        
        :param email: User email
        :type email: str
        :return: Message
        :rtype: dict
        """
        
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await self.session.delete(user)
        await self.session.commit()

        return {"message": "User deleted successfully"}

    async def create_user(self, user: UserCreate):
        """
        Creates a new user
        
        :param user: User object
        :type user: UserCreate
        :return: New user
        :rtype: User
        """
        hashed_password = get_password_hash(user.password)
        user_role = await self.role_repo.get_role_by_name(RoleEnum.USER)
        
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password, role_id = user_role.id, is_active=False)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
    
    
    async def get_user_by_email(self, email):
        """
        Retrieves user by email
        
        :param email: User email
        :type email: str
        :return: User object
        :rtype: User
        """
        
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    
    async def get_user_by_username(self, username):
        """
        Retrieves user by username
        
        :param username: User username
        :type username: str
        :return: User object
        :rtype: User
        """
        
        result = await self.session.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    
    async def activate_user(self, user):
        """
        Activates user when email is confirmed
        
        :param user: User object
        :type user: User
        :return: User object
        :rtype: User
        """
        user.is_active = True
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    

class RoleRepository:
    def __init__(self, session):
        self.session = session
        
    async def get_role_by_name(self, name: RoleEnum):
        """
        Retrieves role by name
        
        :param name: Role name
        :type name: RoleEnum
        :return: Role object
        :rtype: Role
        """
        query = select(Role).filter(Role.name == name.value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()