# QuickNote Project Requirements

## 1. Purpose

QuickNote is a Personal Notes Organization and Management System
designed to keep personal notes in one application. It must provide a
graphical interface and persistent relational database storage.

## 2. Users

The initial version supports personal accounts. Each authenticated user
manages only their own notes and categories.

## 3. Functional Requirements

### FR-01 Registration

The system shall allow a new user to create an account with required
credentials.

### FR-02 Authentication

The system shall authenticate users before allowing access to personal
notes.

### FR-03 Dashboard

The dashboard shall show: - Total number of notes - Number of pinned
notes - Notes grouped/summarized by category - Recent notes or recently
updated notes

### FR-04 Create Note

A user shall create a note containing: - Title - Content - Category -
Priority - Pinned status

### FR-05 View Notes

A user shall view their saved notes through the application.

### FR-06 Edit Note

A user shall update an existing note.

### FR-07 Delete Note

A user shall delete an unnecessary note. Require confirmation before
permanent deletion.

### FR-08 Categories

A user shall organize notes using categories. Initial examples may
include: - School - Personal - Ideas - Reminders

Users should also be able to create their own categories.

### FR-09 Pinning

A user shall pin/unpin important notes.

### FR-10 Priority

A note may have a simple priority such as Low, Normal, or High.

### FR-11 Search

Users shall be able to search their notes by: - Title - Content -
Category

### FR-12 Timestamps

The system shall automatically record: - Created date/time - Last
updated date/time

### FR-13 Reports / Summary

Provide simple summaries such as: - Total notes - Total pinned notes -
Number of notes per category

### FR-14 Logout

Authenticated users shall be able to securely end their application
session.

## 4. Non-Functional Requirements

-   Simple and user-friendly GUI.
-   Persistent SQLite database.
-   Reasonable desktop responsiveness.
-   Clear validation/error messages.
-   Passwords must be hashed.
-   User data must be isolated by account.
-   Code must demonstrate OOP concepts clearly.
-   The application should start locally without requiring internet
    access.

## 5. Scope Boundaries

Do not implement these in the initial version: - Real-time
synchronization across devices - Cloud backup -
Google/Facebook/third-party login - Collaborative/shared notes -
Enterprise team features - Complex note customization

## 6. Acceptance Criteria

A fresh installation must allow the evaluator to register, log in,
create categories and notes, edit them, search/filter them, pin notes,
view summaries, log out, restart the program, and retrieve the same
persisted data.
