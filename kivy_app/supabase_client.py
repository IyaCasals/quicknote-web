from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from config import SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL, WEB_AUTH_BASE_URL


class QuickNoteApiError(Exception):
    pass


@dataclass
class Session:
    access_token: str
    refresh_token: str
    user_id: str
    email: str


class SupabaseClient:
    def __init__(self) -> None:
        self.session: Session | None = None

    @property
    def auth_headers(self) -> dict[str, str]:
        if not self.session:
            raise QuickNoteApiError("Please log in first.")
        return {
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Authorization": f"Bearer {self.session.access_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    @property
    def anon_headers(self) -> dict[str, str]:
        return {
            "apikey": SUPABASE_PUBLISHABLE_KEY,
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> Any:
        if response.ok:
            if not response.text:
                return None
            return response.json()

        try:
            body = response.json()
            message = body.get("error") or body.get("message") or str(body)
        except ValueError:
            message = response.text or "Request failed."
        raise QuickNoteApiError(message)

    def register(self, username: str, email: str, password: str) -> None:
        payload = {
            "email": email.strip().lower(),
            "password": password,
            "data": {"username": username.strip()},
        }
        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=self.anon_headers,
            json=payload,
            timeout=20,
        )
        self._handle_response(response)

    def login(self, identifier: str, password: str) -> Session:
        cleaned = identifier.strip()
        if "@" in cleaned:
            response = requests.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                headers=self.anon_headers,
                json={"email": cleaned.lower(), "password": password},
                timeout=20,
            )
            data = self._handle_response(response)
        else:
            response = requests.post(
                f"{WEB_AUTH_BASE_URL}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json={"identifier": cleaned, "password": password},
                timeout=20,
            )
            data = self._handle_response(response)
            data = data.get("session", data)

        user = data.get("user") or {}
        self.session = Session(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            user_id=user.get("id") or data.get("user_id", ""),
            email=user.get("email") or cleaned,
        )
        return self.session

    def logout(self) -> None:
        self.session = None

    def list_categories(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/categories",
            headers=self.auth_headers,
            params={"select": "*", "order": "name.asc"},
            timeout=20,
        )
        return self._handle_response(response)

    def list_notes(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notes",
            headers=self.auth_headers,
            params={
                "select": "*,categories(id,name)",
                "order": "is_pinned.desc,updated_at.desc",
            },
            timeout=20,
        )
        return self._handle_response(response)

    def create_note(self, note: dict[str, Any]) -> dict[str, Any]:
        payload = {**note, "user_id": self.session.user_id}
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/notes",
            headers=self.auth_headers,
            json=payload,
            timeout=20,
        )
        return self._handle_response(response)[0]

    def update_note(self, note_id: str, note: dict[str, Any]) -> dict[str, Any]:
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/notes",
            headers=self.auth_headers,
            params={"id": f"eq.{note_id}"},
            json=note,
            timeout=20,
        )
        return self._handle_response(response)[0]

    def delete_note(self, note_id: str) -> None:
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/notes",
            headers=self.auth_headers,
            params={"id": f"eq.{note_id}"},
            timeout=20,
        )
        self._handle_response(response)
