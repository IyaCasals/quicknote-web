from datetime import datetime

import customtkinter as ctk

from desktop_app.models.note import PRIORITIES
from desktop_app.views.base_view import BaseView


class NotesView(BaseView):
    def __init__(self, master, controller, query: str = "", pinned_only: bool = False):
        super().__init__(master, controller)
        self.query = query
        self.pinned_only = pinned_only

    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        title = "Pinned Notes" if self.pinned_only else "All Notes"
        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text="+ New Note", command=lambda: self.controller.shell.show_editor()).grid(row=0, column=1, sticky="e")

        filters = ctk.CTkFrame(self, corner_radius=8)
        filters.grid(row=1, column=0, sticky="ew", pady=14)
        filters.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(filters, placeholder_text="Title, content, or category")
        self.search_entry.insert(0, self.query)
        self.search_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        self.category_map = {"All categories": None}
        for category in self.controller.category_manager.list_for_user(self.controller.user_id):
            self.category_map[category.name] = category.id
        self.category_filter = ctk.CTkComboBox(filters, values=list(self.category_map.keys()), width=170)
        self.category_filter.set("All categories")
        self.category_filter.grid(row=0, column=1, padx=8, pady=12)
        self.priority_filter = ctk.CTkComboBox(filters, values=["All", *PRIORITIES], width=120)
        self.priority_filter.set("All")
        self.priority_filter.grid(row=0, column=2, padx=8, pady=12)
        ctk.CTkButton(filters, text="Apply", width=92, command=self._refresh_results).grid(row=0, column=3, padx=12, pady=12)

        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=8)
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self._refresh_results()

    def _refresh_results(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()
        category_id = self.category_map.get(self.category_filter.get())
        priority = self.priority_filter.get()
        notes = self.controller.search_manager.search(
            self.controller.user_id,
            self.search_entry.get(),
            category_id=category_id,
            priority=priority,
            pinned_only=self.pinned_only,
        )
        if not notes:
            ctk.CTkLabel(self.list_frame, text="No matching notes. Create a note or clear the filters.").grid(
                row=0, column=0, padx=16, pady=16, sticky="w"
            )
            return
        for row, note in enumerate(notes):
            card = ctk.CTkFrame(self.list_frame, corner_radius=8)
            card.grid(row=row, column=0, padx=10, pady=8, sticky="ew")
            card.grid_columnconfigure(0, weight=1)
            preview = note.content[:130] + ("..." if len(note.content) > 130 else "")
            category = note.category.name if note.category else "Uncategorized"
            updated = note.updated_at.strftime("%Y-%m-%d %H:%M") if isinstance(note.updated_at, datetime) else ""
            ctk.CTkLabel(card, text=f"{'Pinned - ' if note.is_pinned else ''}{note.title}", font=ctk.CTkFont(size=16, weight="bold")).grid(
                row=0, column=0, padx=14, pady=(12, 2), sticky="w"
            )
            ctk.CTkLabel(card, text=preview or "No content", anchor="w").grid(row=1, column=0, padx=14, pady=2, sticky="w")
            ctk.CTkLabel(card, text=f"{category} | {note.priority} | Updated {updated}").grid(
                row=2, column=0, padx=14, pady=(2, 12), sticky="w"
            )
            ctk.CTkButton(card, text="Edit", width=76, command=lambda note_id=note.id: self.controller.shell.show_editor(note_id)).grid(
                row=0, column=1, rowspan=3, padx=14, pady=14
            )
