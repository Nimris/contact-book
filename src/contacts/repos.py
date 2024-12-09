from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, extract, or_
from datetime import date, timedelta
from fastapi_cache.decorator import cache

from config.cache import custom_repo_key_builder
from src.contacts.models import Contact
from src.contacts.shema import ContactCreate, ContactUpdate


class ContactRepository:
    def __init__(self, session):
        self.session = session


    # @cache(expire=60, namespace='get_contacts_repo', key_builder=custom_repo_key_builder)
    async def get_contacts(self, skip: int, limit: int, owner_id) -> List[Contact]:
        """
        Returns a list of all contacts for a given user with specified pagination
        
        :param skip: Number of contacts to skip
        :type skip: int
        :param limit: Number of contacts to return
        :type limit: int
        :param owner_id: User id
        :type owner_id: int
        :return: List of contacts
        :rtype: List[Contact]
        """
        result = await self.session.execute(select(Contact).where(Contact.owner_id == owner_id).offset(skip).limit(limit))
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found")
        return result.scalars().all()
    
        
    async def get_contact(self, contact_id: int = None) -> Contact:
        """
        Returns a contact based on id
        
        :param contact_id: Contact id
        :type contact_id: int
        :return: Contact
        :rtype: Contact
        """
        
        if contact_id:
            result = await self.session.execute(select(Contact).filter(Contact.id == contact_id))
            return result.scalar_one_or_none()
        return None


    async def create_contact(self, contact: ContactCreate, owner_id: int) -> Contact:
        """
        Creates a new contact for a given user
        
        :param contact: Contact data
        :type contact: ContactCreate
        :param owner_id: User id
        :type owner_id: int
        :return: New contact
        :rtype: Contact
        """
        
        new_contact = Contact(
            name=contact.name, surname=contact.surname, email=contact.email,
            phone=contact.phone, birthday=contact.birthday, owner_id=owner_id
        )
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)
        return new_contact


    async def update_contact(self, contact: ContactUpdate, contact_id: int, owner_id: int) -> Optional[Contact]:
        """
        Updates an existing contact for a given user by provided id
        
        :param contact: Contact data
        :type contact: ContactUpdate
        :param contact_id: Contact id
        :type contact_id: int
        :param owner_id: User id
        :type owner_id: int
        :return: Updated contact
        :rtype: Optional[Contact]
        """
        
        result = await self.session.execute(
            select(Contact).filter(Contact.id == contact_id, Contact.owner_id == owner_id)
        )
        db_contact = result.scalar_one_or_none()
        if db_contact:
            for key, value in contact.model_dump().items():
                if value is not None and hasattr(db_contact, key):
                    setattr(db_contact, key, value)
            await self.session.commit() 
            await self.session.refresh(db_contact)
            return db_contact
        return None
    
    
    async def delete_contact(self, contact_id: int) -> Optional[Contact]:
        """
        Removes an existing contact by provided id
        
        :param contact_id: Contact id
        :type contact_id: int
        :return: Deleted contact
        :rtype: Optional[Contact]
        """
        
        result = await self.session.execute(select(Contact).filter(Contact.id == contact_id))
        db_contact = result.scalar_one_or_none()
        if db_contact:
            await self.session.delete(db_contact)
            await self.session.commit()
        return db_contact


    async def get_upcoming_birthdays(self) -> List[Contact]:
        """
        Returns a list of contacts that have a birthday in the next 7 days
        
        :return: List of contacts
        :rtype: List[Contact]
        """
        
        today = date.today()
        end_date = today + timedelta(days=7)

        query = select(Contact).filter(
            or_(
                and_(
                    extract("month", Contact.birthday) == today.month,
                    extract("day", Contact.birthday) >= today.day
                ),
                and_(
                    extract("month", Contact.birthday) == end_date.month,
                    extract("day", Contact.birthday) <= end_date.day
                ),
                and_(
                    today.month > end_date.month,
                    or_(
                        extract("month", Contact.birthday) == today.month,
                        extract("month", Contact.birthday) == end_date.month
                    )
                )
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()