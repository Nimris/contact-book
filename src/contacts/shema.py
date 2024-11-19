from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ContactBase(BaseModel):
    name: str = Field(max_length=50, example="John")
    surname: str = Field(max_length=50, example="Doe")
    email: str = Field(..., example="example@gmail.com")
    phone: str = Field(max_length=15, example="1234567890")
    birthday: Optional[date] = Field(None, example="2000-06-17")
    

class ContactUpdate(ContactBase):
    pass


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
    