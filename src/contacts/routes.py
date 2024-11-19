
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.utils import get_current_user
from src.database.db import get_db
from src.contacts.shema import ContactCreate, ContactResponse, ContactUpdate
from src.contacts.repos import ContactRepository


router = APIRouter()


@router.get("/all", response_model=List[ContactResponse])
async def get_contacts(db: AsyncSession = Depends(get_db), skip:int = 0, limit:int = 10, user = Depends(get_current_user)):
    contacts = await ContactRepository.get_contacts(db, skip, limit, user.id)
    return contacts


@router.get("/", response_model=List[ContactResponse])
async def get_contact(db: AsyncSession = Depends(get_db), contact_id: Optional[int] = None, name: Optional[str] = None, surname: Optional[str] = None, email: Optional[str] = None):
    contact = await ContactRepository.get_contact(db, contact_id, name, surname, email)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ContactRepository.create_contact(db, contact, user.id)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)):
    contact = await ContactRepository.update_contact(db, contact_id, contact)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await ContactRepository.delete_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/upcoming_birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contacts = await ContactRepository.get_upcoming_birthdays(db)
    return contacts