"""Legacy placeholder.

The thesis Kivy app now uses local SQLite through data_store.py.
This module is kept only so older notes about the previous web-connected
prototype do not point to a missing file.
"""


class QuickNoteApiError(RuntimeError):
    pass


class SupabaseClient:
    def __init__(self) -> None:
        raise QuickNoteApiError("Use QuickNoteStore from data_store.py for the thesis app.")
