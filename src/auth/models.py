from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

# from src.contacts.models import Contact
from config.db import Base

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="owner") 
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True, default=1)
    role: Mapped["Role"] = relationship("Role", lazy="selectin")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)
    avatar: Mapped[str] = mapped_column(String, nullable=True)