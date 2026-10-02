# QuickNote Development Instructions

## Project

**QuickNote -- Personal Notes Organization and Management System**

QuickNote is an academic SDF04 Object-Oriented Programming project.
Build a GUI-based Python application that lets authenticated users
create, organize, search, edit, delete, and pin personal notes.

## Primary Goal

Build a complete, demonstrable application while clearly applying: -
Encapsulation - Inheritance - Polymorphism - Abstraction - Relational
database concepts - CRUD operations

## Required Stack

-   Python 3
-   CustomTkinter for GUI
-   SQLite for the relational database
-   SQLAlchemy ORM
-   Pillow only where images/icons are needed
-   pytest for tests where practical

Do not convert this project into React, Next.js, Node.js, Firebase,
Supabase, or another web/SaaS stack.

## Required Modules

1.  Authentication
2.  Dashboard
3.  Note Management
4.  Category Management
5.  Search
6.  Pin / Priority
7.  Reports / Summary
8.  Account / Logout

## Development Rules

-   Keep the architecture simple enough to explain during a
    thesis/project defense.
-   Every major class must have a clear responsibility.
-   Separate UI, models, business logic/services, and database access.
-   Do not put SQL/database logic directly inside GUI components.
-   Do not use global variables for application state where avoidable.
-   Validate all user input.
-   Handle database and application errors gracefully.
-   Hash passwords; never store plaintext passwords.
-   Each user may access only their own notes and categories.
-   Add comments/docstrings where they help explain OOP decisions.
-   Avoid unnecessary abstractions and enterprise-level complexity.
-   Keep all functionality local. No cloud sync or third-party login is
    required.
-   Make the GUI modern, clean, responsive within reasonable desktop
    window sizes, and easy to demonstrate.

## Suggested Project Structure

``` text
quicknote/
├── main.py
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── note.py
│   │   └── category.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── note_manager.py
│   │   ├── category_manager.py
│   │   ├── search_manager.py
│   │   └── report_generator.py
│   ├── views/
│   │   ├── base_view.py
│   │   ├── login_view.py
│   │   ├── register_view.py
│   │   ├── dashboard_view.py
│   │   ├── notes_view.py
│   │   ├── note_editor.py
│   │   ├── categories_view.py
│   │   └── reports_view.py
│   └── utils/
│       ├── validators.py
│       └── security.py
├── tests/
└── docs/
```

## Definition of Done

The project is complete when a user can: - Register and log in. -
Create, read, update, and delete notes. - Categorize notes. - Pin/unpin
and assign priority to notes. - Search notes by title/content and filter
by category. - See created/updated timestamps. - See dashboard totals,
pinned notes, and category summaries. - View simple reports. - Log
out. - Close and reopen the app without losing stored data.

The implementation must also make the required OOP principles easy to
identify and explain.
