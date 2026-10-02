import re


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_text(value: str, field_name: str, max_length: int | None = None) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required.")
    if max_length and len(cleaned) > max_length:
        raise ValueError(f"{field_name} must be {max_length} characters or fewer.")
    return cleaned


def validate_email(email: str) -> str:
    cleaned = require_text(email, "Email", 255).lower()
    if not EMAIL_RE.match(cleaned):
        raise ValueError("Enter a valid email address.")
    return cleaned


def validate_password(password: str, confirm_password: str | None = None) -> str:
    if len(password or "") < 6:
        raise ValueError("Password must be at least 6 characters.")
    if confirm_password is not None and password != confirm_password:
        raise ValueError("Passwords do not match.")
    return password
