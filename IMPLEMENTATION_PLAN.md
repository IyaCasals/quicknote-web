# QuickNote Implementation Plan

## Phase 1 --- Project Foundation

-   Create project folders.
-   Create virtual environment instructions.
-   Add dependencies.
-   Configure CustomTkinter.
-   Configure SQLite + SQLAlchemy.
-   Implement database initialization.
-   Add application entry point.

**Checkpoint:** Application starts and database file is created.

## Phase 2 --- Models and Database

Implement: - BaseModel - User - Category - Note - Relationships -
Timestamps

Create initialization logic and optional development seed data.

**Checkpoint:** Models can create/read records from SQLite.

## Phase 3 --- Authentication

Implement: - Registration - Password validation - Password hashing -
Login - Logout - User session state - Login/Register UI

**Checkpoint:** A registered user can restart the app and log in.

## Phase 4 --- Main Shell and Dashboard

Implement: - Sidebar navigation - Top header/search area - Dashboard
cards - Recent notes - Category summary

**Checkpoint:** Authenticated user reaches dashboard with correct
account-specific data.

## Phase 5 --- Note CRUD

Implement: - Notes list - Create note - View note - Edit note - Delete
with confirmation - Automatic timestamps - Priority - Pin/unpin

**Checkpoint:** Complete persistent CRUD workflow works.

## Phase 6 --- Categories

Implement: - Category list - Add category - Rename category - Delete
category safely - Assign categories to notes - Default/sample categories
for new users if desired

**Checkpoint:** Notes can be reliably organized by category.

## Phase 7 --- Search and Filtering

Implement: - Search by title/content - Category filtering - Pinned
filtering/view - Optional priority filtering - Clear search/reset

**Checkpoint:** Search returns only the current user's matching notes.

## Phase 8 --- Reports

Implement: - Total notes - Pinned notes - Notes per category -
ReportGenerator service

**Checkpoint:** Report values match database records.

## Phase 9 --- Validation and Testing

Test: - Invalid login - Duplicate username/email - Empty title - Long
content - CRUD - Category operations - Search - Pinning - Ownership/data
isolation - Restart persistence

Fix visual/layout bugs.

## Phase 10 --- Academic Documentation and Demo

Prepare: - README - Installation instructions - ERD - Class diagram -
Application flowchart - Screenshots - OOP explanation - Test cases -
Demo data

## Final Constraint

Do not begin optional enhancements until all required proposal features
work reliably.
