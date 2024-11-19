from fastapi import FastAPI

from src.contacts.routes import router as contacts_router
from src.auth.routes import router as auth_router
from src.database.db import init_db


app = FastAPI()

app.include_router(contacts_router, prefix='/contacts', tags=['contacts'])
app.include_router(auth_router, prefix='/auth', tags=['auth'])


@app.get("/ping")
def pong():
    return {"message": "pong!"}


@app.on_event("startup")
async def on_startup():
    await init_db()
