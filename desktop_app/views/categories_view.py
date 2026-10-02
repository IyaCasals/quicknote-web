import tkinter.messagebox as messagebox

import customtkinter as ctk

from desktop_app.services.exceptions import QuickNoteError
from desktop_app.views.base_view import BaseView


class CategoriesView(BaseView):
    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text="Categories", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 14)
        )

        creator = ctk.CTkFrame(self, corner_radius=8)
        creator.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        creator.grid_columnconfigure(0, weight=1)
        self.name_entry = ctk.CTkEntry(creator, placeholder_text="New category name")
        self.name_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        ctk.CTkButton(creator, text="Add", width=90, command=self._add).grid(row=0, column=1, padx=12, pady=12)

        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=8)
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self._load_categories()

    def _load_categories(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()
        rows = self.controller.category_manager.counts_for_user(self.controller.user_id)
        if not rows:
            ctk.CTkLabel(self.list_frame, text="No categories yet. Add one above.").grid(
                row=0, column=0, padx=16, pady=16, sticky="w"
            )
        for row, (category, count) in enumerate(rows):
            item = ctk.CTkFrame(self.list_frame, corner_radius=8)
            item.grid(row=row, column=0, padx=10, pady=8, sticky="ew")
            item.grid_columnconfigure(0, weight=1)
            entry = ctk.CTkEntry(item)
            entry.insert(0, category.name)
            entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
            ctk.CTkLabel(item, text=f"{count} notes").grid(row=0, column=1, padx=8)
            ctk.CTkButton(
                item,
                text="Rename",
                width=86,
                command=lambda category_id=category.id, field=entry: self._rename(category_id, field.get()),
            ).grid(row=0, column=2, padx=6)
            ctk.CTkButton(
                item,
                text="Delete",
                width=76,
                fg_color="#8a2d2d",
                hover_color="#6f2424",
                command=lambda category_id=category.id: self._delete(category_id),
            ).grid(row=0, column=3, padx=12)

    def _add(self) -> None:
        try:
            self.controller.category_manager.create(self.controller.user_id, self.name_entry.get())
            self.name_entry.delete(0, "end")
            self.show_success("Category added.")
            self._load_categories()
        except (QuickNoteError, ValueError) as exc:
            self.show_error(str(exc))

    def _rename(self, category_id: int, name: str) -> None:
        try:
            self.controller.category_manager.update(self.controller.user_id, category_id, name)
            self.show_success("Category renamed.")
            self._load_categories()
        except (QuickNoteError, ValueError) as exc:
            self.show_error(str(exc))

    def _delete(self, category_id: int) -> None:
        if messagebox.askyesno("Delete category", "Delete this category? Existing notes will become uncategorized."):
            self.controller.category_manager.delete(self.controller.user_id, category_id)
            self.show_success("Category deleted.")
            self._load_categories()
