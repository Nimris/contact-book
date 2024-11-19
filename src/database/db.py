from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# docker run --name contact-book-app -p 5432:5432 -e POSTGRES_PASSWORD=567234 -d postgres
# docker exec -it contact-book-app psql -U postgres -c "CREATE DATABASE contact_book_app;"
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:567234@localhost:5432/contact_book_app"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()