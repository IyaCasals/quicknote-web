# QuickNote UI/UX Specification

## Design Direction

Create a clean, modern desktop notes application using CustomTkinter.

The UI should feel like a lightweight modern productivity app, not a
collection of disconnected Tkinter forms.

## Main Layout

``` text
┌──────────────────────────────────────────────────────────────┐
│ QuickNote                    Search Notes...       User      │
├────────────────┬─────────────────────────────────────────────┤
│ Dashboard      │                                             │
│ All Notes      │             PAGE CONTENT                    │
│ Pinned         │                                             │
│ Categories     │                                             │
│ Reports        │                                             │
│                │                                             │
│ Logout         │                                  + New Note │
└────────────────┴─────────────────────────────────────────────┘
```

## Authentication

### Login

-   QuickNote logo/title
-   Username/email
-   Password
-   Login button
-   Link/button to Register
-   Inline/friendly errors

### Registration

-   Username
-   Email
-   Password
-   Confirm password
-   Register
-   Back to login

## Dashboard

Display summary cards: - Total Notes - Pinned Notes - Total Categories

Below summaries: - Recent Notes - Notes by Category

## Notes Screen

Top: - Search input - Category filter - Priority filter if implemented -
`+ New Note`

Note cards/list items show: - Title - Short content preview - Category -
Priority - Pin indicator - Updated date

Pinned notes should appear prominently or sort before unpinned notes.

## Note Editor

Fields: - Title - Content (large text area) - Category selector -
Priority selector - Pinned checkbox/toggle

Actions: - Save - Cancel - Delete only when editing an existing note

## Categories

Show category list and note count. Allow: - Create category - Rename
category - Delete category with confirmation and safe handling of
assigned notes

## Reports

Keep reports simple: - Total notes - Pinned notes - Notes per category

Charts are optional; clear counts are sufficient.

## Interaction Rules

-   Confirm destructive actions.
-   Disable or prevent invalid saves.
-   Show clear success/error feedback.
-   Empty states should explain what to do, e.g. "No notes yet. Create
    your first note."
-   Avoid opening excessive windows. Prefer changing content within the
    main application shell.
-   Support a reasonable minimum window size.
