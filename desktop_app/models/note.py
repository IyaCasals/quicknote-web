from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from desktop_app.models.base import BaseModel, TimestampMixin


PRIORITIES = ("Low", "Normal", "High")


class Note(TimestampMixin, BaseModel):
    __tablename__ = "notes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="Normal", nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="notes")
    category = relationship("Category", back_populates="notes")

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Note title is required.")
        if self.priority not in PRIORITIES:
            raise ValueError("Priority must be Low, Normal, or High.")

    def update_content(self, title: str, content: str) -> None:
        self.title = title.strip()
        self.content = content.strip()
        self.validate()

    def set_priority(self, priority: str) -> None:
        self.priority = priority
        self.validate()

    def pin(self) -> None:
        self.is_pinned = True

    def unpin(self) -> None:
        self.is_pinned = False
