# QuickNote One-Shot Build Prompt

Read and follow all project Markdown specifications before writing code:

-   `CLAUDE.md`
-   `PROJECT_REQUIREMENTS.md`
-   `ARCHITECTURE.md`
-   `DATABASE_SCHEMA.md`
-   `OOP_DESIGN.md`
-   `UI_UX.md`
-   `IMPLEMENTATION_PLAN.md`

Build **QuickNote -- Personal Notes Organization and Management System**
as a complete Python desktop GUI application.

## Execution Instructions

1.  Inspect all specification files first.
2.  Create a concise implementation plan and verify that it covers every
    requirement.
3.  Build the application phase-by-phase without asking for confirmation
    between normal implementation steps.
4.  Use Python, CustomTkinter, SQLite, and SQLAlchemy.
5.  Keep the architecture clearly object-oriented and suitable for an
    SDF04 academic project.
6.  Implement authentication, dashboard, note CRUD, categories, search,
    pin/priority, timestamps, reports, and logout.
7.  Hash passwords and isolate each user's records.
8.  Use a modern desktop UI with sidebar navigation and reusable view
    components.
9.  Add validation, confirmations, empty states, and understandable
    error handling.
10. Add useful tests for core business logic.
11. Add `requirements.txt`.
12. Add a comprehensive `README.md` with setup and run instructions.
13. Seed/demo data may be provided through a clearly optional
    development mechanism; do not hard-code demo records into production
    startup.
14. Run tests and fix errors.
15. Run a final requirements audit against every Markdown specification.

## Quality Requirements

-   No placeholder buttons for required features.
-   No fake data in production screens when real database values should
    be shown.
-   No plaintext passwords.
-   No raw SQL inside GUI views.
-   No cross-user access.
-   No unnecessary cloud dependencies.
-   Avoid overengineering.
-   Use clear naming and readable code.
-   Keep the OOP principles easy to identify for presentation/defense.

## Final Response

When finished, report: - Files created - Features completed - OOP
principles and where they are demonstrated - Database tables - Tests
performed/results - Exact commands to install dependencies and run the
application - Any remaining limitations

Do not claim a feature is complete unless it actually works.
