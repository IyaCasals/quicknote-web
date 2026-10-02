import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from desktop_app.models.base import Base
from desktop_app.services import AuthService, CategoryManager, NoteManager, ReportGenerator, SearchManager
from desktop_app.services.exceptions import AuthenticationError, NotFoundError, ValidationError


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def services(session):
    return {
        "auth": AuthService(session),
        "notes": NoteManager(session),
        "categories": CategoryManager(session),
        "search": SearchManager(session),
        "reports": ReportGenerator(session),
    }


def test_register_hashes_password_and_login_works(services):
    user = services["auth"].register("matt", "matt@example.com", "secret1", "secret1")

    assert user.password_hash != "secret1"
    assert services["auth"].login("matt", "secret1").id == user.id
    with pytest.raises(AuthenticationError):
        services["auth"].login("matt", "wrongpass")


def test_duplicate_username_or_email_is_rejected(services):
    services["auth"].register("matt", "matt@example.com", "secret1", "secret1")

    with pytest.raises(ValidationError):
        services["auth"].register("matt", "other@example.com", "secret1", "secret1")


def test_note_crud_pin_search_and_reports(services):
    user = services["auth"].register("matt", "matt@example.com", "secret1", "secret1")
    category = services["categories"].create(user.id, "Work")
    note = services["notes"].create(user.id, "Launch list", "Email supplier", category.id, "High", True)

    found = services["search"].search(user.id, "supplier")
    assert [item.id for item in found] == [note.id]
    assert services["reports"].summary(user.id)["pinned_notes"] == 1

    services["notes"].update(user.id, note.id, "Launch list v2", "Confirm stock", category.id, "Normal", False)
    updated = services["notes"].get(user.id, note.id)
    assert updated.title == "Launch list v2"
    assert updated.priority == "Normal"
    assert not updated.is_pinned

    services["notes"].delete(user.id, note.id)
    with pytest.raises(NotFoundError):
        services["notes"].get(user.id, note.id)


def test_user_data_is_isolated(services):
    user_one = services["auth"].register("one", "one@example.com", "secret1", "secret1")
    user_two = services["auth"].register("two", "two@example.com", "secret1", "secret1")
    note = services["notes"].create(user_one.id, "Private", "Only user one can see this")

    assert services["search"].search(user_two.id, "Private") == []
    with pytest.raises(NotFoundError):
        services["notes"].get(user_two.id, note.id)


def test_deleting_category_uncategorizes_notes(services):
    user = services["auth"].register("matt", "matt@example.com", "secret1", "secret1")
    category = services["categories"].create(user.id, "Temporary")
    note = services["notes"].create(user.id, "Draft", "Body", category.id)

    services["categories"].delete(user.id, category.id)

    assert services["notes"].get(user.id, note.id).category_id is None
