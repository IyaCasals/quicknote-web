import tkinter.messagebox as messagebox

import customtkinter as ctk

from desktop_app.models.note import PRIORITIES
from desktop_app.services.exceptions import QuickNoteError
from desktop_app.views.base_view import BaseView


class NoteEditor(BaseView):
    def __init__(self, master, controller, note_id: int | None = None):
        super().__init__(master, controller)
        self.note_id = note_id
        self.note = None

    def render(self) -> None:
        self.clear()
        if self.note_id:
            self.note = self.controller.note_manager.get(self.controller.user_id, self.note_id)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(
            self,
            text="Edit Note" if self.note else "New Note",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 14))

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Title")
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.content_box = ctk.CTkTextbox(self, height=260)
        self.content_box.grid(row=3, column=0, sticky="nsew", pady=10)

        meta = ctk.CTkFrame(self, corner_radius=8)
        meta.grid(row=2, column=0, sticky="ew")
        self.category_map = {"Uncategorized": None}
        for category in self.controller.category_manager.list_for_user(self.controller.user_id):
            self.category_map[category.name] = category.id
        self.category_select = ctk.CTkComboBox(meta, values=list(self.category_map.keys()), width=180)
        self.category_select.grid(row=0, column=0, padx=12, pady=12)
        self.priority_select = ctk.CTkComboBox(meta, values=list(PRIORITIES), width=120)
        self.priority_select.grid(row=0, column=1, padx=8, pady=12)
        self.pinned_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(meta, text="Pinned", variable=self.pinned_var).grid(row=0, column=2, padx=8, pady=12)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        ctk.CTkButton(buttons, text="Save", command=self._save).pack(side="left")
        ctk.CTkButton(buttons, text="Cancel", fg_color="transparent", command=self.controller.shell.show_notes).pack(side="left", padx=8)
        if self.note:
            ctk.CTkButton(buttons, text="Delete", fg_color="#8a2d2d", hover_color="#6f2424", command=self._delete).pack(side="right")
        self._load_note()

    def _load_note(self) -> None:
        self.priority_select.set("Normal")
        self.category_select.set("Uncategorized")
        if not self.note:
            return
        self.title_entry.insert(0, self.note.title)
        self.content_box.insert("1.0", self.note.content)
        self.priority_select.set(self.note.priority)
        self.pinned_var.set(self.note.is_pinned)
        if self.note.category:
            self.category_select.set(self.note.category.name)

    def _save(self) -> None:
        try:
            category_id = self.category_map.get(self.category_select.get())
            if self.note:
                self.controller.note_manager.update(
                    self.controller.user_id,
                    self.note.id,
                    self.title_entry.get(),
                    self.content_box.get("1.0", "end").strip(),
                    category_id,
                    self.priority_select.get(),
                    self.pinned_var.get(),
                )
                self.show_success("Note updated.")
            else:
                self.controller.note_manager.create(
                    self.controller.user_id,
                    self.title_entry.get(),
                    self.content_box.get("1.0", "end").strip(),
                    category_id,
                    self.priority_select.get(),
                    self.pinned_var.get(),
                )
                self.show_success("Note created.")
            self.controller.shell.show_notes()
        except (QuickNoteError, ValueError) as exc:
            self.show_error(str(exc))

    def _delete(self) -> None:
        if not self.note:
            return
        if messagebox.askyesno("Delete note", "Delete this note permanently?"):
            self.controller.note_manager.delete(self.controller.user_id, self.note.id)
            self.show_success("Note deleted.")
            self.controller.shell.show_notes()
