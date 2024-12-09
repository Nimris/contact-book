import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.contacts.repos import ContactRepository
from src.contacts.models import Contact
from src.contacts.shema import ContactCreate, ContactUpdate
from src.contacts.models import User
from datetime import date, timedelta


class TestContacts(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.user = User(id=1)
        self.repo = ContactRepository(self.session)
        
        
    async def test_get_contacts(self):
        contacts = [Contact(id=1, owner_id=1), Contact(id=2, owner_id=1), Contact(id=3, owner_id=1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = contacts
        self.session.execute = AsyncMock(return_value=mock_result)
        
        result = await self.repo.get_contacts(skip=0, limit=10, owner_id=self.user.id)
        self.assertEqual(result, contacts)
        
        
    async def test_get_contact(self):
        contact = Contact(id=1, name="John", surname="Doe", email="john.doe@example.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact
        self.session.execute = AsyncMock(return_value=mock_result)
        
        result = await self.repo.get_contact(contact_id=1)
        self.assertEqual(result, contact)
        
        
    async def test_get_contact_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute = AsyncMock(return_value=mock_result)
        
        result = await self.repo.get_contact(contact_id=1)
        self.assertEqual(result, None)
        
        
    async def test_create_contact(self):
        contact_data = ContactCreate(
            name="John", surname="Doe", email="john.doe@example.com",
            phone="1234567890", birthday="1990-01-01"
        )
        owner_id = 1
        new_contact = Contact(
            name=contact_data.name, surname=contact_data.surname, email=contact_data.email,
            phone=contact_data.phone, birthday=contact_data.birthday, owner_id=owner_id
        )
        
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await self.repo.create_contact(contact_data, owner_id)

        self.session.add.assert_called_once()
        added_contact = self.session.add.call_args[0][0]
        self.assertEqual(added_contact.name, contact_data.name)
        self.assertEqual(added_contact.surname, contact_data.surname)
        self.assertEqual(added_contact.email, contact_data.email)
        self.assertEqual(added_contact.phone, contact_data.phone)
        self.assertEqual(added_contact.birthday, contact_data.birthday)
        self.assertEqual(added_contact.owner_id, owner_id)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(added_contact)
        self.assertIs(result, added_contact)
        
    
    async def test_update_contact(self):
        owner_id = 1
        contact_id = 101
        contact_update = ContactUpdate(name="Jane", surname="Dooe", email="jane.doe@example.com", phone="1234567890")
        existing_contact = Contact(
            id=contact_id, owner_id=owner_id, name="John", surname="Doe", email="john.doe@example.com", phone="1234567890"
        )
        updated_contact = Contact(
            id=contact_id, owner_id=owner_id, name="Jane", surname="Dooe", email="jane.doe@example.com", phone="1234567890"
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_contact
        self.session.execute = AsyncMock(return_value=mock_result)
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        
        result = await self.repo.update_contact(contact_update, contact_id, owner_id)
        
        executed_query = self.session.execute.call_args[0][0]
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(existing_contact)
        self.assertEqual(result.name, updated_contact.name)
        self.assertEqual(result.surname, updated_contact.surname)
        self.assertEqual(result.email, updated_contact.email)
        self.assertEqual(result.phone, updated_contact.phone)
        self.assertEqual(result.owner_id, updated_contact.owner_id)
        
        
    async def test_delete_contact(self):
        contact_id = 101
        existing_contact = Contact(id=contact_id, name="Jane", surname="Dooe", email="jane.doe@example.com", phone="1234567890")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_contact
        self.session.execute = AsyncMock(return_value=mock_result)
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()
        
        result = await self.repo.delete_contact(contact_id)

        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(executed_query.compile().params, {"id_1": contact_id})
        self.session.delete.assert_awaited_once_with(existing_contact)
        self.session.commit.assert_awaited_once()
        self.assertEqual(result, existing_contact)
        
        
    async def test_upcoming_birthdays(self):
        today = date.today()
        end_date = today + timedelta(days=7)
        
        contacts = [
            Contact(id=1, name="Alice", birthday=date(today.year, today.month, today.day + 1)),
            Contact(id=2, name="Bob", birthday=date(today.year, end_date.month, end_date.day - 1)),
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = contacts
        self.session.execute = AsyncMock(return_value=mock_result)

        result = await self.repo.get_upcoming_birthdays()

        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        
        self.assertIn("EXTRACT(month FROM contacts.birthday)", str(executed_query))
        self.assertIn("EXTRACT(day FROM contacts.birthday)", str(executed_query))
        
        self.assertEqual(result, contacts)
        
if __name__ == '__main__':
    unittest.main()