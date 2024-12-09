import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.auth.utils import RoleChecker
from config.db import get_db
from main import app
from src.contacts.models import Contact
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_db():
    db = MagicMock(AsyncSession)
    return db


@pytest.fixture
def mock_role_checker():
    return MagicMock(return_value=True)


@pytest.fixture
def client(mock_db, mock_role_checker):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[RoleChecker] = lambda roles: mock_role_checker
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_contact(client, mock_db):
    contact = Contact(id=1, name="John", surname="Doe", email="ads@das.com")
    mock_repo = MagicMock()
    mock_repo.get_contact = MagicMock(return_value=contact)
    
    mock_db.return_value = mock_repo
    
    response = client.get("/contacts/", params={"id": 1})
    
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "John", "surname": "Doe", "email": "ads@das.com"}


@pytest.mark.asyncio
async def test_get_contact_not_found(client, mock_db):
    mock_repo = MagicMock()
    mock_repo.get_contact = MagicMock(return_value=None)
    
    mock_db.return_value = mock_repo

    response = client.get("/contacts/", params={"id": 999})

    assert response.status_code == 404