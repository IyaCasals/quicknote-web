# QuickNote OOP Design

## Goal

The implementation must visibly demonstrate encapsulation, inheritance,
abstraction, and polymorphism because these are core academic
requirements.

## Core Classes

### BaseModel

Abstract/common parent for persistent domain models.

Common behavior: - `id` - timestamps where appropriate - common
representation/helper behavior

### User

Represents an application user.

Responsibilities: - User identity/profile data - Relationships to owned
notes/categories

Do not store plaintext passwords.

### Note

Represents a personal note.

Properties: - title - content - category - priority - pinned state -
timestamps

Possible methods: - `pin()` - `unpin()` - `update_content()` -
`set_priority()` - `validate()`

### Category

Represents a user-defined note category.

### BaseManager

Abstract base class for common manager/repository behavior.

Possible abstract methods: - `create()` - `get()` - `update()` -
`delete()`

### NoteManager

Handles note CRUD, pinning, priority, and ownership checks.

### CategoryManager

Handles category CRUD and category validation.

### AuthService

Handles: - registration - password hashing - credential verification -
authentication state support

### SearchManager

Searches notes belonging to the current user.

### ReportGenerator

Generates summary data for dashboard/reports.

## Demonstrating OOP Principles

### Encapsulation

Keep object state and related behavior together. Business rules belong
in model/service methods rather than scattered through GUI event
handlers.

Example:

``` python
note.set_priority("High")
note.pin()
```

### Inheritance

Use meaningful parent classes rather than artificial inheritance.

``` text
BaseModel
├── User
├── Note
└── Category

BaseView
├── LoginView
├── DashboardView
├── NotesView
└── ReportsView
```

### Abstraction

Expose clear service interfaces so the GUI does not need to know how
database operations are implemented.

Example:

``` python
note_manager.create_note(...)
```

instead of running SQL inside a button callback.

### Polymorphism

Derived views may implement/override a common method such as:

``` python
def render(self):
    ...
```

Each view renders differently through the same interface.

Managers/models may similarly override shared validation or
representation behavior where it naturally fits.

## Defense Guidance

The code should make it easy to point to exact files/classes and
explain: 1. Where data is encapsulated. 2. Which classes inherit from a
base class. 3. Which interfaces/abstract methods hide implementation
details. 4. Which overridden methods demonstrate polymorphism.

Never add inheritance solely to claim OOP compliance; it must serve a
clear design purpose.
