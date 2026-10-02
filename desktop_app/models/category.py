from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from desktop_app.models.base import BaseModel, TimestampMixin


class Category(TimestampMixin, BaseModel):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_category_user_name"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)

    user = relationship("User", back_populates="categories")
    notes = relationship("Note", back_populates="category")
