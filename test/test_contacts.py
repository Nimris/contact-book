from unittest.mock import AsyncMock, MagicMock
from httpx import ASGITransport, AsyncClient
import pytest
from src.contacts.models import Contact
from main import app
from fastapi import status
from src.contacts.repos import ContactRepository


@pytest.mark.asyncio
async def test_create_contact(test_user, auth_header, override_get_db, monkeypatch):
    user_id = test_user.id
    mock_cache = AsyncMock()
    monkeypatch.setattr("src.contacts.routes.invalidate_get_contacts_repo_cache", mock_cache)      
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/contacts", json={
            "name": "John",
            "surname": "Doe",
            "email": "john@ghfg.com",
            "phone_number": "08012345678",
            "birthday": "1990-01-01",
        }, headers=auth_header)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John"
        assert data["surname"] == "Doe"
        mock_cache.assert_called_once_with(user_id)
    
      
@pytest.mark.asyncio
async def test_get_contact(override_get_db: Contact, test_user_contact, auth_header, monkeypatch):
    mock_cache = AsyncMock()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/contacts/{test_user_contact.id}", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_user_contact.first_name
        assert data["surname"] == test_user_contact.last_name
        