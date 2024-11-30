from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from config.cache import invalidate_get_contacts_repo_cache
from src.auth.shema import RoleEnum
from src.auth.utils import RoleChecker, get_current_user
from config.db import get_db
from src.contacts.shema import ContactCreate, ContactResponse, ContactUpdate
from src.contacts.repos import ContactRepository


router = APIRouter()


@router.get("/all", 
            response_model=List[ContactResponse], 
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60)),],
            )
async def get_contacts(
    db: AsyncSession = Depends(get_db), 
    skip:int = 0, 
    limit:int = 10,
    user = Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN]))
    ):
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_contacts(skip, limit, user.id)
    return contacts


@router.get("/", 
            response_model=List[ContactResponse], 
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60)),],
            )
async def get_contact(db: AsyncSession = Depends(get_db), user = Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])), contact_id: Optional[int] = None, name: Optional[str] = None, surname: Optional[str] = None, email: Optional[str] = None):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id, name, surname, email)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    await invalidate_get_contacts_repo_cache(user.id)  
    return contact


@router.post("/", response_model=ContactResponse, 
             status_code=status.HTTP_201_CREATED, 
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def create_contact(contact: ContactCreate, user = Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])), db: AsyncSession = Depends(get_db)):
    await invalidate_get_contacts_repo_cache(user.id)
    contact_repo = ContactRepository(db)
    contact = await contact_repo.create_contact(contact, user.id)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])),
):
    contact_repo = ContactRepository(db)
    updated_contact = await contact_repo.update_contact(contact, contact_id, user.id)
    if updated_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # await invalidate_get_contacts_repo_cache(user.id)
    return updated_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.delete_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # await invalidate_get_contacts_repo_cache(user.id)
    return contact


@router.get("/upcoming_birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_upcoming_birthdays()
    return contacts