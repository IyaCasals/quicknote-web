# QuickNote Architecture

## Architectural Style

Use a simple layered desktop architecture:

``` text
Presentation / Views
        ↓
Services / Managers
        ↓
Models / Domain Objects
        ↓
Database / SQLAlchemy
        ↓
SQLite
```

GUI components should call services/managers. Views must not contain raw
database queries.

## Application Flow

``` text
Start Application
      ↓
Initialize Database
      ↓
Login / Register
      ↓
Authenticated Session
      ↓
Main Application Shell
 ┌────┼───────────┬──────────┐
Dashboard       Notes     Categories
                  │
            Search/Filter
                  │
              Reports
                  ↓
                Logout
```

## Responsibilities

### `database.py`

-   SQLAlchemy engine
-   Session factory
-   Database initialization
-   Safe session handling

### Models

Represent database/domain entities: - BaseModel - User - Note - Category

### Services

Business logic: - AuthService - NoteManager - CategoryManager -
SearchManager - ReportGenerator

### Views

Only presentation and user interaction: - LoginView - RegisterView -
DashboardView - NotesView - NoteEditor - CategoriesView - ReportsView

## State

Maintain the authenticated user's ID/session in the application
controller. Never allow views to arbitrarily change ownership IDs.

## Error Handling

Services should raise understandable application/domain errors. Views
catch them and display friendly messages rather than stack traces.

## Startup

`main.py` should: 1. Load configuration. 2. Initialize the database. 3.
Create the main CustomTkinter application. 4. Show authentication. 5.
Enter the GUI event loop.

## Simplicity Requirement

This is an academic OOP application. Prefer readable, explainable code
over advanced patterns that make the application difficult to defend.
