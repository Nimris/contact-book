from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User
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
    """
    Returns a list of all contacts for a given user with specified pagination
    
    :param db: Database session
    :type db: AsyncSession
    :param skip: Number of contacts to skip
    :type skip: int
    :param limit: Number of contacts to return
    :type limit: int
    :param user: User object
    :type user: User
    :return: List of contacts
    :rtype: List[Contact]
    """
    
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_contacts(skip, limit, user.id)
    return contacts


@router.get("/", 
            response_model=ContactResponse, 
            description='No more than 10 requests per minute',
            # dependencies=[Depends(RateLimiter(times=10, seconds=60)),],
            )
async def get_contact(db: AsyncSession = Depends(get_db), user = Depends(get_current_user), contact_id: int = None):
    """
    Returns a list of contacts based on the provided parameters
    
    :param db: Database session
    :type db: AsyncSession
    :param contact_id: Contact id
    :type contact_id: int
    :return: List of contacts
    :rtype: Contact
    """
    
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # await invalidate_get_contacts_repo_cache(user.id)
    return contact


@router.post("/", response_model=ContactResponse, 
             status_code=status.HTTP_201_CREATED, 
            #  description='No more than 10 requests per minute',
            #  dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def create_contact(
    contact: ContactCreate, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
    ):
    """
    Creates a new contact for a given user
    
    :param contact: Contact object
    :type contact: ContactCreate
    :param user: User object
    :type user: User
    :param db: Database session
    :type db: AsyncSession
    :return: Contact object
    :rtype: Contact
    """
    contact_repo = ContactRepository(db)
    await invalidate_get_contacts_repo_cache(user.id)
    contact = await contact_repo.create_contact(contact, user.id)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])),
):
    """
    Updates a user's contact
    
    :param contact_id: Contact id
    :type contact_id: int
    :param contact: Contact object
    :type contact: ContactUpdate
    :param db: Database session
    :type db: AsyncSession
    :param user: User object
    :type user: User
    :return: Updated contact
    :rtype: Contact
    """
    
    contact_repo = ContactRepository(db)
    updated_contact = await contact_repo.update_contact(contact, contact_id, user.id)
    if updated_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # await invalidate_get_contacts_repo_cache(user.id)
    return updated_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    """
    Deletes a user's contact
    
    :param contact_id: Contact id
    :type contact_id: int
    :param db: Database session
    :type db: AsyncSession
    :param user: User object
    :type user: User
    :return: Contact object
    :rtype: None
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.delete_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # await invalidate_get_contacts_repo_cache(user.id)
    return contact


@router.get("/upcoming_birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    Returns a list of contacts that have birthdays in the next 7 days
    
    :param db: Database session
    :type db: AsyncSession
    :return: List of contacts
    :rtype: List[Contact]
    """
    contact_repo = ContactRepository(db)
    contacts = await contact_repo.get_upcoming_birthdays()
    return contacts