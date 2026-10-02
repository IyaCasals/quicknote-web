from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from desktop_app.models.category import Category
from desktop_app.models.note import Note
from desktop_app.services.base_manager import BaseManager
from desktop_app.services.exceptions import NotFoundError, ValidationError
from desktop_app.utils.validators import require_text


class CategoryManager(BaseManager):
    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, user_id: int, name: str) -> Category:
        name = require_text(name, "Category name", 80)
        category = Category(user_id=user_id, name=name)
        self._session.add(category)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise ValidationError("You already have a category with that name.") from exc
        return category

    def get(self, user_id: int, category_id: int) -> Category:
        category = self._session.scalar(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )
        if not category:
            raise NotFoundError("Category not found.")
        return category

    def list_for_user(self, user_id: int) -> list[Category]:
        return list(
            self._session.scalars(
                select(Category).where(Category.user_id == user_id).order_by(Category.name.asc())
            )
        )

    def counts_for_user(self, user_id: int) -> list[tuple[Category, int]]:
        rows = self._session.execute(
            select(Category, func.count(Note.id))
            .outerjoin(Note, (Note.category_id == Category.id) & (Note.user_id == user_id))
            .where(Category.user_id == user_id)
            .group_by(Category.id)
            .order_by(Category.name.asc())
        ).all()
        return [(category, count) for category, count in rows]

    def update(self, user_id: int, category_id: int, name: str) -> Category:
        category = self.get(user_id, category_id)
        category.name = require_text(name, "Category name", 80)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise ValidationError("You already have a category with that name.") from exc
        return category

    def delete(self, user_id: int, category_id: int) -> None:
        category = self.get(user_id, category_id)
        for note in list(category.notes):
            if note.user_id == user_id:
                note.category_id = None
        self._session.delete(category)
        self._session.commit()
