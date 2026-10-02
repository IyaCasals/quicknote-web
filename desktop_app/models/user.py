from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from desktop_app.models.base import BaseModel, TimestampMixin


class User(TimestampMixin, BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
