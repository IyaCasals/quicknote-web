# QuickNote Database Schema

## Database

SQLite via SQLAlchemy ORM.

## Entity Relationship Overview

``` text
USER 1 ───────< CATEGORY
  │
  └───────────< NOTE >────── 0..1 CATEGORY
```

A user owns many notes and categories. A note belongs to exactly one
user and may belong to one category.

## `users`

  Column          Type       Rules
  --------------- ---------- ---------------------
  id              Integer    PK, auto increment
  username        String     required, unique
  email           String     required, unique
  password_hash   String     required
  created_at      DateTime   required, automatic

## `categories`

  Column       Type       Rules
  ------------ ---------- -----------------------
  id           Integer    PK
  user_id      Integer    FK users.id, required
  name         String     required
  created_at   DateTime   automatic

Constraint: category names should be unique per user where practical.

## `notes`

  Column        Type       Rules
  ------------- ---------- ----------------------------
  id            Integer    PK
  user_id       Integer    FK users.id, required
  category_id   Integer    FK categories.id, nullable
  title         String     required
  content       Text       required/default empty
  priority      String     Low/Normal/High
  is_pinned     Boolean    default false
  created_at    DateTime   automatic
  updated_at    DateTime   automatic/update on edit

## Optional `activity_logs`

Only implement if the core application is already complete.

  Column       Type
  ------------ ----------------------
  id           Integer PK
  user_id      Integer FK
  note_id      Integer FK, nullable
  action       String
  created_at   DateTime

## Data Rules

-   Every query for notes/categories must be scoped to the logged-in
    `user_id`.
-   Deleting a category must not accidentally delete a user's notes.
    Either prevent deletion when in use or set the note category to NULL
    after confirmation.
-   Deleting a user is not required in the initial project.
-   Use ORM parameters rather than constructing SQL from user input.
