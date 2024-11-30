import os
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from src.contacts.routes import router as contacts_router
from src.auth.routes import router as auth_router
from config.db import init_db
from config.general import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(contacts_router, prefix='/contacts', tags=['contacts'])
app.include_router(auth_router, prefix='/auth', tags=['auth'])


@app.get("/ping")
def pong():
    return {"message": "pong!"}


@app.on_event("startup")
async def on_startup():
    await init_db()

    redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )

    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    await FastAPILimiter.init(redis)


@app.on_event("shutdown")
async def on_shutdown():
    redis = FastAPICache.get_backend()._client
    await redis.close()
    
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)