from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio


from src.contacts.routes import router as contacts_router
from src.auth.routes import router as auth_router
from config.db import init_db
from config.general import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = asyncio.from_url(settings.redis_url, encoding="utf-8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()

app = FastAPI(lifespan=lifespan)

app.include_router(contacts_router, prefix='/contacts', tags=['contacts'])
app.include_router(auth_router, prefix='/auth', tags=['auth'])


@app.get("/ping")
def pong():
    return {"message": "pong!"}


@app.on_event("startup")
async def on_startup():
    await init_db()
