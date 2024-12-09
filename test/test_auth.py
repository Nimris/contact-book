from unittest.mock import patch
from fastapi import BackgroundTasks
from httpx import ASGITransport, AsyncClient
from src.auth.models import Role
from main import app
import pytest


@pytest.mark.asyncio
async def test_register_user(user_role: Role, override_get_db, faker, monkeypatch):

    with patch.object(BackgroundTasks, 'add_task'):
        # mock_send_email = MagicMock()
        # monkeypatch.setattr("src.auth.mail_utils.send_verification_email", mock_send_email)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "email": faker.email(),
                "username": faker.user_name(),
                "password": faker.password(),
            }
            
            response = await ac.post("/auth/register", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data['email'] == payload['email']
            assert data['username'] == payload['username']
            assert data.get("password") is None
            assert data["id"] is not None


@pytest.mark.asyncio
async def test_user_login(override_get_db, test_user, user_password):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/token",
            data={"username": test_user.username, "password": user_password},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data