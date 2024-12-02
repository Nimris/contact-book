import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException

from src.auth.utils import create_access_token, create_refresh_token, create_verification_token, decode_access_token, decode_verification_token, get_current_user
from src.auth.pass_utilits import verify_password
from src.auth.shema import Token, UserCreate, UserResponse
from src.auth.repos import UserRepository
from config.db import get_db
from src.auth.mail_utils import send_verification_email 
from config.general import settings


router = APIRouter()
env = Environment(loader=FileSystemLoader('src/templates'))


@router.get("/me/", response_model=UserResponse)
async def user_me(current_user = Depends(get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar(file: UploadFile = File(), 
                             current_user = Depends(get_current_user),
                             db = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    r = cloudinary.uploader.upload(file.file, public_id=f'ContactApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user_repo = UserRepository(db)
    user = await user_repo.update_avatar(current_user.email, src_url)
    return user


@router.delete("/delete-user/{email}")
async def delete_user(email: str, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    response = await user_repo.delete_user(email)
    return response


@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(user_create.email)
    
    if user:
        raise HTTPException(status_code=409, detail="User already registered")
   
    user = await user_repo.create_user(user_create)
    verification_token = create_verification_token(user.email)
    verification_url = f"http://localhost:8000/auth/verify-email?token={verification_token}"
    template = env.get_template("verification_email.html")
    email_body = template.render(verification_url=verification_url)
    background_tasks.add_task(send_verification_email, user.email, email_body)
    
    return user


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = decode_verification_token(token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_repo.activate_user(user)
    return {"message": "User successfully activated"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(form_data.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_tokens(refresh_token: str, db: AsyncSession = Depends(get_db)):
    token_data = decode_access_token(refresh_token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
