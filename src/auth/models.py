from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

# from src.contacts.models import Contact
from src.database.db import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="owner") 