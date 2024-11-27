from enum import Enum
from pydantic import BaseModel, EmailStr


class RoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"
    

class UserBase(BaseModel):
    username: str
    email: EmailStr
    

class UserCreate(UserBase):
    password: str
    
    
class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
    
    
class TokenData(BaseModel):
    username: str | None = None
    
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str