from pathlib import Path

import pytest

from kivy_app.data_store import DEFAULT_CATEGORIES, QuickNoteError, QuickNoteStore


@pytest.fixture()
def store(tmp_path: Path):
    database = tmp_path / "quicknote.db"
    service = QuickNoteStore(database)
    try:
        yield service
    finally:
        service.close()


def test_register_hashes_password_and_seeds_categories(store):
    user_id = store.register("matt", "matt@example.com", "secret1")
    user = store.authenticate("matt", "secret1")
    categories = store.list_categories(user_id)

    assert user["id"] == user_id
    assert [category["name"] for category in categories] == sorted(DEFAULT_CATEGORIES)
    with pytest.raises(QuickNoteError):
        store.authenticate("matt", "wrong-password")


def test_note_crud_search_and_reports(store):
    user_id = store.register("matt", "matt@example.com", "secret1")
    category_id = store.create_category(user_id, "Thesis")
    note_id = store.create_note(
        user_id,
        {
            "title": "Defense checklist",
            "content": "Prepare diagrams and demo script",
            "category_id": category_id,
            "priority": "High",
            "is_pinned": True,
        },
    )

    found = store.list_notes(user_id, search="demo")
    summary = store.dashboard(user_id)

    assert [note["id"] for note in found] == [note_id]
    assert summary["total_notes"] == 1
    assert summary["pinned_notes"] == 1
    assert summary["notes_by_category"]["Thesis"] == 1

    store.update_note(
        user_id,
        note_id,
        {
            "title": "Defense checklist updated",
            "content": "Prepare final demo script",
            "category_id": category_id,
            "priority": "Normal",
            "is_pinned": False,
        },
    )
    updated = store.list_notes(user_id, search="updated")[0]

    assert updated["priority"] == "Normal"
    assert not updated["is_pinned"]

    store.delete_note(user_id, note_id)
    assert store.list_notes(user_id) == []


def test_user_data_is_isolated(store):
    user_one = store.register("one", "one@example.com", "secret1")
    user_two = store.register("two", "two@example.com", "secret1")
    store.create_note(user_one, {"title": "Private", "content": "Only one"})

    assert store.list_notes(user_two, search="Private") == []


def test_deleting_category_uncategorizes_notes(store):
    user_id = store.register("matt", "matt@example.com", "secret1")
    category_id = store.create_category(user_id, "Temporary")
    store.create_note(user_id, {"title": "Draft", "content": "Body", "category_id": category_id})

    store.delete_category(user_id, category_id)
    note = store.list_notes(user_id)[0]

    assert note["category_id"] is None
    assert note["category_name"] == "Uncategorized"
