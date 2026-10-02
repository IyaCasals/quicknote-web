class QuickNoteError(Exception):
    """Base class for friendly application errors."""


class AuthenticationError(QuickNoteError):
    pass


class NotFoundError(QuickNoteError):
    pass


class ValidationError(QuickNoteError):
    pass
