from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from desktop_app.models.category import Category
from desktop_app.models.note import Note, PRIORITIES
from desktop_app.services.base_manager import BaseManager
from desktop_app.services.exceptions import NotFoundError, ValidationError
from desktop_app.utils.validators import require_text


class NoteManager(BaseManager):
    def __init__(self, session: Session):
        super().__init__(session)

    def _validate_category(self, user_id: int, category_id: int | None) -> int | None:
        if category_id is None:
            return None
        exists = self._session.scalar(
            select(Category.id).where(Category.id == category_id, Category.user_id == user_id)
        )
        if not exists:
            raise ValidationError("Selected category does not exist.")
        return category_id

    def create(
        self,
        user_id: int,
        title: str,
        content: str = "",
        category_id: int | None = None,
        priority: str = "Normal",
        is_pinned: bool = False,
    ) -> Note:
        title = require_text(title, "Title", 160)
        if priority not in PRIORITIES:
            raise ValidationError("Priority must be Low, Normal, or High.")
        note = Note(
            user_id=user_id,
            title=title,
            content=(content or "").strip(),
            category_id=self._validate_category(user_id, category_id),
            priority=priority,
            is_pinned=bool(is_pinned),
        )
        note.validate()
        self._session.add(note)
        self._session.commit()
        return note

    def get(self, user_id: int, note_id: int) -> Note:
        note = self._session.scalar(
            select(Note)
            .options(joinedload(Note.category))
            .where(Note.id == note_id, Note.user_id == user_id)
        )
        if not note:
            raise NotFoundError("Note not found.")
        return note

    def list_for_user(
        self,
        user_id: int,
        category_id: int | None = None,
        priority: str | None = None,
        pinned_only: bool = False,
        limit: int | None = None,
    ) -> list[Note]:
        query = select(Note).options(joinedload(Note.category)).where(Note.user_id == user_id)
        if category_id:
            query = query.where(Note.category_id == category_id)
        if priority and priority != "All":
            query = query.where(Note.priority == priority)
        if pinned_only:
            query = query.where(Note.is_pinned.is_(True))
        query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        if limit:
            query = query.limit(limit)
        return list(self._session.scalars(query))

    def update(
        self,
        user_id: int,
        note_id: int,
        title: str,
        content: str,
        category_id: int | None,
        priority: str,
        is_pinned: bool,
    ) -> Note:
        note = self.get(user_id, note_id)
        note.update_content(require_text(title, "Title", 160), content or "")
        note.category_id = self._validate_category(user_id, category_id)
        note.set_priority(priority)
        note.is_pinned = bool(is_pinned)
        self._session.commit()
        return note

    def delete(self, user_id: int, note_id: int) -> None:
        note = self.get(user_id, note_id)
        self._session.delete(note)
        self._session.commit()

    def set_pinned(self, user_id: int, note_id: int, pinned: bool) -> Note:
        note = self.get(user_id, note_id)
        note.pin() if pinned else note.unpin()
        self._session.commit()
        return note
