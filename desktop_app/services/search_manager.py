from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from desktop_app.models.category import Category
from desktop_app.models.note import Note


class SearchManager:
    def __init__(self, session: Session):
        self._session = session

    def search(
        self,
        user_id: int,
        query_text: str = "",
        category_id: int | None = None,
        priority: str | None = None,
        pinned_only: bool = False,
    ) -> list[Note]:
        query = select(Note).options(joinedload(Note.category)).where(Note.user_id == user_id)
        cleaned = (query_text or "").strip()
        if cleaned:
            pattern = f"%{cleaned}%"
            query = query.outerjoin(Category).where(
                or_(Note.title.ilike(pattern), Note.content.ilike(pattern), Category.name.ilike(pattern))
            )
        if category_id:
            query = query.where(Note.category_id == category_id)
        if priority and priority != "All":
            query = query.where(Note.priority == priority)
        if pinned_only:
            query = query.where(Note.is_pinned.is_(True))
        query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        return list(self._session.scalars(query))
