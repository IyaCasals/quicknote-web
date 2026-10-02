from sqlalchemy import func, select
from sqlalchemy.orm import Session

from desktop_app.models.category import Category
from desktop_app.models.note import Note


class ReportGenerator:
    def __init__(self, session: Session):
        self._session = session

    def summary(self, user_id: int) -> dict:
        total_notes = self._session.scalar(select(func.count(Note.id)).where(Note.user_id == user_id)) or 0
        pinned_notes = (
            self._session.scalar(select(func.count(Note.id)).where(Note.user_id == user_id, Note.is_pinned.is_(True)))
            or 0
        )
        total_categories = (
            self._session.scalar(select(func.count(Category.id)).where(Category.user_id == user_id)) or 0
        )
        category_rows = self._session.execute(
            select(Category.name, func.count(Note.id))
            .outerjoin(Note, (Note.category_id == Category.id) & (Note.user_id == user_id))
            .where(Category.user_id == user_id)
            .group_by(Category.id)
            .order_by(Category.name.asc())
        ).all()
        uncategorized = (
            self._session.scalar(
                select(func.count(Note.id)).where(Note.user_id == user_id, Note.category_id.is_(None))
            )
            or 0
        )
        notes_by_category = {name: count for name, count in category_rows}
        if uncategorized:
            notes_by_category["Uncategorized"] = uncategorized
        return {
            "total_notes": total_notes,
            "pinned_notes": pinned_notes,
            "total_categories": total_categories,
            "notes_by_category": notes_by_category,
        }
