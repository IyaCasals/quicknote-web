from __future__ import annotations

import hashlib
import secrets
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_CATEGORIES = ["School", "Personal", "Ideas", "Reminders"]
PRIORITIES = ["Low", "Normal", "High"]


class QuickNoteError(Exception):
    """Application-level error shown to the user."""


class QuickNoteStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self) -> None:
        self.connection.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL COLLATE NOCASE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, name),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Normal'
                    CHECK (priority IN ('Low', 'Normal', 'High')),
                is_pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_notes_user_updated
                ON notes(user_id, is_pinned DESC, updated_at DESC);

            CREATE INDEX IF NOT EXISTS idx_categories_user
                ON categories(user_id, name);
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def register(self, username: str, email: str, password: str) -> int:
        username = username.strip()
        email = email.strip().lower()
        self._validate_user_input(username, email, password)

        try:
            with self.connection:
                cursor = self.connection.execute(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (username, email, hash_password(password)),
                )
                user_id = int(cursor.lastrowid)
                self._seed_categories(user_id)
                return user_id
        except sqlite3.IntegrityError as exc:
            message = str(exc).lower()
            if "users.username" in message:
                raise QuickNoteError("Username is already taken.") from exc
            if "users.email" in message:
                raise QuickNoteError("Email is already registered.") from exc
            raise QuickNoteError("Account could not be created.") from exc

    def authenticate(self, identifier: str, password: str) -> dict[str, Any]:
        identifier = identifier.strip()
        if not identifier or not password:
            raise QuickNoteError("Username/email and password are required.")

        row = self.connection.execute(
            """
            SELECT id, username, email, password_hash
            FROM users
            WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE
            """,
            (identifier, identifier),
        ).fetchone()

        if not row or not verify_password(password, row["password_hash"]):
            raise QuickNoteError("Invalid login details.")

        return self._row(row)

    def list_categories(self, user_id: int) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT
                categories.id,
                categories.name,
                categories.created_at,
                COUNT(notes.id) AS note_count
            FROM categories
            LEFT JOIN notes
                ON notes.category_id = categories.id
                AND notes.user_id = categories.user_id
            WHERE categories.user_id = ?
            GROUP BY categories.id
            ORDER BY categories.name
            """,
            (user_id,),
        ).fetchall()
        return [self._row(row) for row in rows]

    def create_category(self, user_id: int, name: str) -> int:
        name = self._clean_name(name)
        try:
            with self.connection:
                cursor = self.connection.execute(
                    "INSERT INTO categories (user_id, name) VALUES (?, ?)",
                    (user_id, name),
                )
                return int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise QuickNoteError("Category already exists.") from exc

    def rename_category(self, user_id: int, category_id: int, name: str) -> None:
        name = self._clean_name(name)
        try:
            with self.connection:
                cursor = self.connection.execute(
                    "UPDATE categories SET name = ? WHERE id = ? AND user_id = ?",
                    (name, category_id, user_id),
                )
                if cursor.rowcount == 0:
                    raise QuickNoteError("Category not found.")
        except sqlite3.IntegrityError as exc:
            raise QuickNoteError("Category already exists.") from exc

    def delete_category(self, user_id: int, category_id: int) -> None:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM categories WHERE id = ? AND user_id = ?",
                (category_id, user_id),
            )
            if cursor.rowcount == 0:
                raise QuickNoteError("Category not found.")

    def list_notes(
        self,
        user_id: int,
        search: str = "",
        category_id: int | None = None,
        priority: str | None = None,
        pinned_only: bool = False,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                notes.id,
                notes.user_id,
                notes.category_id,
                notes.title,
                notes.content,
                notes.priority,
                notes.is_pinned,
                notes.created_at,
                notes.updated_at,
                categories.name AS category_name
            FROM notes
            LEFT JOIN categories
                ON categories.id = notes.category_id
                AND categories.user_id = notes.user_id
            WHERE notes.user_id = ?
        """
        params: list[Any] = [user_id]

        cleaned_search = search.strip()
        if cleaned_search:
            query += """
                AND (
                    notes.title LIKE ?
                    OR notes.content LIKE ?
                    OR categories.name LIKE ?
                )
            """
            pattern = f"%{cleaned_search}%"
            params.extend([pattern, pattern, pattern])

        if category_id is not None:
            query += " AND notes.category_id = ?"
            params.append(category_id)

        if priority:
            query += " AND notes.priority = ?"
            params.append(priority)

        if pinned_only:
            query += " AND notes.is_pinned = 1"

        query += " ORDER BY notes.is_pinned DESC, notes.updated_at DESC"
        rows = self.connection.execute(query, params).fetchall()
        return [self._note_row(row) for row in rows]

    def create_note(self, user_id: int, payload: dict[str, Any]) -> int:
        data = self._validate_note_payload(payload)
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO notes
                    (user_id, category_id, title, content, priority, is_pinned)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    data["category_id"],
                    data["title"],
                    data["content"],
                    data["priority"],
                    int(data["is_pinned"]),
                ),
            )
            return int(cursor.lastrowid)

    def update_note(self, user_id: int, note_id: int, payload: dict[str, Any]) -> None:
        data = self._validate_note_payload(payload)
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE notes
                SET category_id = ?,
                    title = ?,
                    content = ?,
                    priority = ?,
                    is_pinned = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (
                    data["category_id"],
                    data["title"],
                    data["content"],
                    data["priority"],
                    int(data["is_pinned"]),
                    note_id,
                    user_id,
                ),
            )
            if cursor.rowcount == 0:
                raise QuickNoteError("Note not found.")

    def delete_note(self, user_id: int, note_id: int) -> None:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM notes WHERE id = ? AND user_id = ?",
                (note_id, user_id),
            )
            if cursor.rowcount == 0:
                raise QuickNoteError("Note not found.")

    def dashboard(self, user_id: int) -> dict[str, Any]:
        notes = self.list_notes(user_id)
        categories = self.list_categories(user_id)
        totals_by_category = Counter(note["category_name"] for note in notes)
        return {
            "total_notes": len(notes),
            "pinned_notes": sum(1 for note in notes if note["is_pinned"]),
            "total_categories": len(categories),
            "recent_notes": notes[:5],
            "notes_by_category": dict(sorted(totals_by_category.items())),
        }

    def _seed_categories(self, user_id: int) -> None:
        for category in DEFAULT_CATEGORIES:
            self.connection.execute(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)",
                (user_id, category),
            )

    def _validate_user_input(self, username: str, email: str, password: str) -> None:
        if len(username) < 3:
            raise QuickNoteError("Username must be at least 3 characters.")
        if "@" not in email or "." not in email:
            raise QuickNoteError("Enter a valid email address.")
        if len(password) < 6:
            raise QuickNoteError("Password must be at least 6 characters.")

    def _clean_name(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise QuickNoteError("Category name is required.")
        if len(name) > 40:
            raise QuickNoteError("Category name must be 40 characters or fewer.")
        return name

    def _validate_note_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title", "")).strip()
        content = str(payload.get("content", "")).strip()
        priority = str(payload.get("priority", "Normal"))
        category_id = payload.get("category_id")

        if not title:
            raise QuickNoteError("Title is required.")
        if len(title) > 120:
            raise QuickNoteError("Title must be 120 characters or fewer.")
        if priority not in PRIORITIES:
            raise QuickNoteError("Priority must be Low, Normal, or High.")

        return {
            "title": title,
            "content": content,
            "priority": priority,
            "category_id": category_id,
            "is_pinned": bool(payload.get("is_pinned", False)),
        }

    def _note_row(self, row: sqlite3.Row) -> dict[str, Any]:
        data = self._row(row)
        data["is_pinned"] = bool(data["is_pinned"])
        data["category_name"] = data["category_name"] or "Uncategorized"
        return data

    def _row(self, row: sqlite3.Row) -> dict[str, Any]:
        return dict(row)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, expected = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return secrets.compare_digest(digest.hex(), expected)
