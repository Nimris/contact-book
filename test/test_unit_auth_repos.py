import unittest
from unittest.mock import AsyncMock, MagicMock
import bcrypt
from fastapi import HTTPException
from sqlalchemy.future import select
from src.auth.models import User, Role
from src.auth.shema import RoleEnum, UserCreate
from src.auth.repos import UserRepository, RoleRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.pass_utilits import get_password_hash


import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        
        self.role_repo = MagicMock(spec=RoleRepository)
        self.repo = UserRepository(self.session)
        
        self.session.add = AsyncMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.session.execute = AsyncMock()

        
    async def test_update_avatar(self):
        email = "test@example.com"
        new_url = "http://new-avatar-url.com"

        user = MagicMock(spec=User)
        user.email = email
        user.avatar = "http://old-avatar-url.com"

        self.repo.get_user_by_email = AsyncMock(return_value=user)
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()

        updated_user = await self.repo.update_avatar(email, new_url)

        self.repo.get_user_by_email.assert_awaited_once_with(email)
        self.session.add.assert_called_once_with(user)
        self.session.commit.assert_awaited_once()
        self.assertEqual(updated_user.avatar, new_url)


    async def test_delete_user_not_found(self):
        email = "nonexistent@example.com"
        
        self.repo.get_user_by_email = AsyncMock(return_value=None)

        with self.assertRaises(HTTPException) as context:
            await self.repo.delete_user(email)
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")


    async def test_delete_user_success(self):
        email = "test@example.com"
        user = MagicMock(spec=User)
        
        self.repo.get_user_by_email = AsyncMock(return_value=user)
        
        response = await self.repo.delete_user(email)
        
        self.repo.get_user_by_email.assert_awaited_once_with(email)
        self.session.delete.assert_awaited_once_with(user)
        self.session.commit.assert_awaited_once()
        self.assertEqual(response, {"message": "User deleted successfully"})

    
    async def test_create_user(self):       
        user_data = UserCreate(username="testuser", email="test@example.com", password="password")
        hashed_password = get_password_hash(user_data.password)
        user_role = MagicMock(spec=Role)
        user_role.id = 1
        
        role_repo_mock = MagicMock(spec=RoleRepository)
        role_repo_mock.get_role_by_name = AsyncMock(return_value=user_role)
        print("Mocked role returned:", await role_repo_mock.get_role_by_name(RoleEnum.USER))
        
        self.repo.role_repo = role_repo_mock
        
        self.session.add = AsyncMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        
        result = await self.repo.create_user(user_data)
        
        new_user = User(
            username=user_data.username, 
            email=user_data.email, 
            hashed_password=hashed_password, 
            role_id=user_role.id, 
            is_active=False, 
            )
        
        self.session.add.assert_called_once()
        added_user = self.session.add.call_args[0][0]
        self.assertEqual(added_user.username, user_data.username)
        self.assertEqual(added_user.email, user_data.email)
        self.assertTrue(bcrypt.checkpw(user_data.password.encode('utf-8'), added_user.hashed_password.encode('utf-8')))
        self.assertEqual(added_user.role_id, user_role.id)
        self.assertFalse(added_user.is_active)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(added_user)
        self.assertIs(result, added_user)
        
        
    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = MagicMock(spec=User)
        
        self.repo.get_user_by_email = AsyncMock(return_value=user)
        
        result = await self.repo.get_user_by_email(email)
        
        self.repo.get_user_by_email.assert_awaited_once_with(email)
        self.assertEqual(result, user)


    async def test_get_user_by_username(self):
        username = "testuser"
        user = MagicMock(spec=User)
        
        self.repo.get_user_by_username = AsyncMock(return_value=user)
        
        result = await self.repo.get_user_by_username(username)
        
        self.repo.get_user_by_username.assert_awaited_once_with(username)
        self.assertEqual(result, user)
        
    
    async def test_activate_user(self):
        user = MagicMock(spec=User)
        user.is_active = False
        
        activated_user = await self.repo.activate_user(user)
        
        self.session.add.assert_called_once_with(user)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()
        self.assertTrue(activated_user.is_active)
        

class TestRoleRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
            
    async def test_get_role_by_name(self):
        role_name = RoleEnum.USER
        role_mock = MagicMock(spec=Role)
        role_mock.name = role_name.value

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=role_mock)
        self.session.execute = AsyncMock(return_value=mock_result)

        repo = RoleRepository(self.session)

        result = await repo.get_role_by_name(role_name)

        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0] 
        self.assertEqual(str(executed_query), str(select(Role).filter(Role.name == role_name.value)))
        self.assertEqual(result, role_mock)
        
        
    async def test_get_role_by_name_not_found(self):
        role_name = RoleEnum.USER

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        self.session.execute = AsyncMock(return_value=mock_result)

        repo = RoleRepository(self.session)

        result = await repo.get_role_by_name(role_name)

        self.session.execute.assert_awaited_once()

        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(select(Role).filter(Role.name == role_name.value)))

        self.assertIsNone(result)
        

if __name__ == '__main__':
    unittest.main()
