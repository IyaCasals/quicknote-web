from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from desktop_app.models.category import Category
from desktop_app.models.user import User
from desktop_app.services.exceptions import AuthenticationError, ValidationError
from desktop_app.utils.security import hash_password, verify_password
from desktop_app.utils.validators import require_text, validate_email, validate_password


DEFAULT_CATEGORIES = ("School", "Personal", "Ideas", "Reminders")


class AuthService:
    def __init__(self, session: Session):
        self._session = session

    def register(self, username: str, email: str, password: str, confirm_password: str) -> User:
        username = require_text(username, "Username", 80)
        email = validate_email(email)
        password = validate_password(password, confirm_password)

        user = User(username=username, email=email, password_hash=hash_password(password))
        self._session.add(user)
        try:
            self._session.flush()
            for category_name in DEFAULT_CATEGORIES:
                self._session.add(Category(user_id=user.id, name=category_name))
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise ValidationError("Username or email is already registered.") from exc
        return user

    def login(self, identifier: str, password: str) -> User:
        identifier = require_text(identifier, "Username or email")
        user = self._session.scalar(
            select(User).where(or_(User.username == identifier, User.email == identifier.lower()))
        )
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid username/email or password.")
        return user
