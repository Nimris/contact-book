from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, extract, or_
from datetime import date, timedelta

from src.contacts.models import Contact
from src.contacts.shema import ContactCreate, ContactUpdate


class ContactRepository:
    
    def __init__(self, session):
        self.session = session

    async def get_contacts(self, skip: int, limit: int, owner_id) -> List[Contact]:
        result = await self.execute(select(Contact).where(Contact.owner_id == owner_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_contact(self, contact_id: Optional[int] = None, name: Optional[str] = None, surname: Optional[str] = None, email: Optional[str] = None) -> List[Contact]:
        if contact_id:
            result = await self.execute(select(Contact).filter(Contact.id == contact_id))
            return result.scalars().all()
        if name:
            result = await self.execute(select(Contact).filter(Contact.name == name))
            return result.scalars().all()
        if surname:
            result = await self.execute(select(Contact).filter(Contact.surname == surname))
            return result.scalars().all()
        if email:
            result = await self.execute(select(Contact).filter(Contact.email == email))
            return result.scalars().all()
        return []

    async def create_contact(self, contact: ContactCreate, owner_id: int) -> Contact:
        new_contact = Contact(
            name=contact.name, surname=contact.surname, email=contact.email,
            phone=contact.phone, birthday=contact.birthday, owner_id=owner_id
        )
        self.add(new_contact)
        await self.commit()
        await self.refresh(new_contact)
        return new_contact

    async def update_contact(self, contact_id: int, contact: ContactUpdate) -> Optional[Contact]:
        result = await self.execute(select(Contact).filter(Contact.id == contact_id))
        db_contact = result.scalar_one_or_none()
        if db_contact:
            db_contact.name = contact.name
            db_contact.surname = contact.surname
            db_contact.email = contact.email
            db_contact.phone = contact.phone
            db_contact.birthday = contact.birthday
            await self.commit()
            await self.refresh(db_contact)
        return db_contact

    async def delete_contact(self, contact_id: int) -> Optional[Contact]:
        result = await self.execute(select(Contact).filter(Contact.id == contact_id))
        db_contact = result.scalar_one_or_none()
        if db_contact:
            await self.delete(db_contact)
            await self.commit()
        return db_contact

    async def get_upcoming_birthdays(self) -> List[Contact]:
        today = date.today()
        end_date = today + timedelta(days=7)
        
        query = select(Contact).filter(
            or_(
                and_(
                    extract('month', Contact.birthday) == today.month,
                    extract('day', Contact.birthday) >= today.day,
                    extract('day', Contact.birthday) <= end_date.day
                ),
                and_(
                    extract('month', Contact.birthday) == end_date.month,
                    extract('day', Contact.birthday) <= end_date.day
                )
            )
        )
        
        result = await self.execute(query)
        return result.scalars().all()