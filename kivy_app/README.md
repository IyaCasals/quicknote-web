# QuickNote Kivy Mobile App

This is the thesis-compliant QuickNote application. It is a local
Python/Kivy app that stores data in SQLite through Python's built-in
`sqlite3` connector.

## Thesis Tech Stack

- Programming Language: Python
- GUI Framework: Kivy
- Database: SQLite
- Database Connector Library: sqlite3
- IDE/Editor: VSCode or PyCharm
- Version Control: Git and GitHub
- Other Libraries: Pillow, reportlab

## Features

- Local register/login with username or email.
- Password hashing with PBKDF2.
- Starter categories: School, Personal, Ideas, Reminders.
- Dashboard with totals, pinned notes, recent notes, and category summaries.
- Register with username, email, and password.
- View notes in a mobile list.
- Create, edit, delete, pin, and prioritize notes.
- Create, rename, and delete categories.
- Category deletion keeps notes and marks them as Uncategorized.
- Search notes by title, content, or category.
- Export a PDF report.
- Data persists locally in `quicknote.db`.

## Local Desktop Run

```bash
cd kivy_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The SQLite database is created automatically inside Kivy's application
data directory.

## APK Build

Buildozer works best on Linux or WSL Ubuntu, not native Windows.

```bash
cd kivy_app
pip install buildozer
buildozer android debug
```

The APK will be created under:

```text
kivy_app/bin/
```

## Testing

From the repository root:

```bash
python -m pytest tests/test_kivy_store.py
```

## Notes

The hosted Next.js/Supabase app is kept as a separate web version. This
Kivy app is the version aligned with the Python GUI thesis requirement.
