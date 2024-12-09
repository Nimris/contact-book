from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.auth.shema import RoleEnum, TokenData
from jose import jwt
from fastapi import HTTPException
from config.db import get_db
from src.auth.repos import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from config.general import settings


ALGORYTHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
SECRET_KEY = settings.secret_key
VERIFICATION_TOKEN_EXPIRE_HOURS = 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_verification_token(email:str):
    """
    Creates a verification token
    
    :param email: User email
    :type email: str
    :return: Verification token
    :rtype: str
    """
    
    expire = datetime.now(timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORYTHM)
    return encoded_jwt

def decode_verification_token(token):
    """
    Decodes a verification token
    
    :param token: Verification token
    :type token: str
    :return: User email
    :rtype: str
    """
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORYTHM])
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.JWTError:
        return None


def create_access_token(data: dict):
    """
    Creates an access token
    
    :param data: Data to encode
    :type data: dict
    :return: Access token
    :rtype: str
    """
    
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORYTHM) 


def create_refresh_token(data: dict):
    """
    Creates a refresh token
    
    :param data: Data to encode
    :type data: dict
    :return: Refresh token
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORYTHM)


def decode_access_token(token):
    """
    Decodes an access token
    
    :param token: Access token
    :type token: str
    :return: Token data
    :rtype: TokenData
    """
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORYTHM])
        username = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except jwt.JWTError:
        return None
        
        
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Retrieves current user
    
    :param token: Access token
    :type token: str
    :param db: Database session
    :type db: AsyncSession
    :return: User object
    :rtype: User
    """
    
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user_repo = UserRepository(db)  
    user = await user_repo.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles
        
    async def __call__(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        Checks if user has the required role
        
        :param token: Access token
        :type token: str
        :param db: Database session
        :type db: AsyncSession
        :return: User object
        :rtype: User
        """
        
        user = await get_current_user(token, db)
        
        if RoleEnum(user.role.name) not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        return user
        
    