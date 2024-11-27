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
        result = await self.session.execute(select(Contact).where(Contact.owner_id == owner_id).offset(skip).limit(limit))
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found")
        return result.scalars().all()
    
        
    async def get_contact(self, contact_id: Optional[int] = None, name: Optional[str] = None, surname: Optional[str] = None, email: Optional[str] = None) -> List[Contact]:
        if contact_id:
            result = await self.session.execute(select(Contact).filter(Contact.id == contact_id))
            return result.scalars().all()
        if name:
            result = await self.session.execute(select(Contact).filter(Contact.name == name))
            return result.scalars().all()
        if surname:
            result = await self.session.execute(select(Contact).filter(Contact.surname == surname))
            return result.scalars().all()
        if email:
            result = await self.session.execute(select(Contact).filter(Contact.email == email))
            return result.scalars().all()
        return []


    async def create_contact(self, contact: ContactCreate, owner_id: int) -> Contact:
        new_contact = Contact(
            name=contact.name, surname=contact.surname, email=contact.email,
            phone=contact.phone, birthday=contact.birthday, owner_id=owner_id
        )
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)
        return new_contact


    async def update_contact(self, contact: ContactUpdate, contact_id: int, owner_id: int) -> Optional[Contact]:
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
        result = await self.session.execute(select(Contact).filter(Contact.id == contact_id))
        db_contact = result.scalar_one_or_none()
        if db_contact:
            await self.session.delete(db_contact)
            await self.session.commit()
        return db_contact


    async def get_upcoming_birthdays(self) -> List[Contact]:
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