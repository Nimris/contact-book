from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.auth.pass_utilits import get_password_hash
from src.auth.shema import RoleEnum
from src.auth.utils import RoleChecker, create_access_token, create_refresh_token
from src.contacts.models import Contact
from src.auth.models import User, Role

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from fastapi_limiter.depends import RateLimiter

from config.db import Base, get_db
from config.general import settings
from main import app

DATABASE_URL = settings.database_test_url

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)

    

@pytest_asyncio.fixture(scope='function')
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
        
@pytest_asyncio.fixture(scope='function')
async def db_session(setup_database):
    async with AsyncSessionLocal() as session:
        yield session
        
        
@pytest_asyncio.fixture(scope='function')
async def override_get_db(db_session):
    async def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
    


@pytest_asyncio.fixture(scope='function')
async def user_role(db_session):
    role = Role(
        id=1,
        name=RoleEnum.USER.value,
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope='function')
async def user_password(faker):
    return faker.password()


@pytest_asyncio.fixture(scope='function')
async def test_user(db_session, faker, user_role, user_password):
    hashed_password = get_password_hash(user_password)
    user = User(
        email=faker.email(),
        username=faker.user_name(),
        hashed_password=hashed_password,
        role_id=user_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope='function')
async def auth_header(test_user: User):
    access_token = create_access_token({"sub": test_user.username})
    refresh_token = create_refresh_token({"sub": test_user.username})
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Refresh-Token": f"{refresh_token}",
    }
    return headers


@pytest_asyncio.fixture(scope='function')
async def test_user_contact(db_session, test_user, faker):
    contact = Contact(
        name=faker.first_name(),
        surname=faker.last_name(),
        phone=faker.phone_number(),
        email=faker.email(),
        owner_id=test_user.id,
        birthday=faker.date_of_birth(),
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)
    return contact

@pytest_asyncio.fixture(scope="function")
async def override_rate_limiter():
    app.dependency_overrides[RateLimiter] = lambda *args, **kwargs: None
    yield
    app.dependency_overrides.clear()
    
@pytest_asyncio.fixture
def mock_contact_repo():
    mock_repo = AsyncMock()
    mock_repo.get_contact.return_value = [
        Contact(id=1, name="John", surname="Doe", email="john.doe@example.com")
    ]
    return mock_repo