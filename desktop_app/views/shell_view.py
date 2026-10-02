import customtkinter as ctk

from desktop_app.views.base_view import BaseView
from desktop_app.views.categories_view import CategoriesView
from desktop_app.views.dashboard_view import DashboardView
from desktop_app.views.note_editor import NoteEditor
from desktop_app.views.notes_view import NotesView
from desktop_app.views.reports_view import ReportsView


class ShellView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.content_frame: ctk.CTkFrame | None = None
        self.message_label: ctk.CTkLabel | None = None
        self.search_entry: ctk.CTkEntry | None = None

    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, height=64, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="QuickNote", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=22, pady=16, sticky="w"
        )
        self.search_entry = ctk.CTkEntry(header, placeholder_text="Search notes...")
        self.search_entry.grid(row=0, column=1, padx=12, pady=14, sticky="ew")
        self.search_entry.bind("<Return>", lambda _event: self.show_notes(query=self.search_entry.get()))
        ctk.CTkButton(header, text="Search", width=92, command=lambda: self.show_notes(query=self.search_entry.get())).grid(
            row=0, column=2, padx=8, pady=14
        )
        ctk.CTkLabel(header, text=self.controller.current_user.username).grid(row=0, column=3, padx=18, pady=14)

        sidebar = ctk.CTkFrame(self, width=170, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("All Notes", self.show_notes),
            ("Pinned", lambda: self.show_notes(pinned_only=True)),
            ("Categories", self.show_categories),
            ("Reports", self.show_reports),
        ]
        for row, (text, command) in enumerate(buttons):
            ctk.CTkButton(sidebar, text=text, command=command, anchor="w").grid(
                row=row, column=0, padx=14, pady=(14 if row == 0 else 6, 0), sticky="ew"
            )
        sidebar.grid_rowconfigure(6, weight=1)
        ctk.CTkButton(sidebar, text="Logout", fg_color="#8a2d2d", hover_color="#6f2424", command=self.controller.logout).grid(
            row=7, column=0, padx=14, pady=16, sticky="ew"
        )

        main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main.grid(row=1, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        self.message_label = ctk.CTkLabel(main, text="", anchor="w")
        self.message_label.grid(row=0, column=0, padx=18, pady=(10, 0), sticky="ew")
        self.content_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=18)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.show_dashboard()

    def set_message(self, message: str, error: bool = False) -> None:
        if self.message_label:
            self.message_label.configure(text=message, text_color="#b42318" if error else "#087443")

    def _swap_content(self, view: BaseView) -> None:
        if not self.content_frame:
            return
        for child in self.content_frame.winfo_children():
            child.destroy()
        view.grid(row=0, column=0, sticky="nsew")
        view.render()

    def show_dashboard(self) -> None:
        self._swap_content(DashboardView(self.content_frame, self.controller))

    def show_notes(self, query: str = "", pinned_only: bool = False) -> None:
        self._swap_content(NotesView(self.content_frame, self.controller, query=query, pinned_only=pinned_only))

    def show_editor(self, note_id: int | None = None) -> None:
        self._swap_content(NoteEditor(self.content_frame, self.controller, note_id=note_id))

    def show_categories(self) -> None:
        self._swap_content(CategoriesView(self.content_frame, self.controller))

    def show_reports(self) -> None:
        self._swap_content(ReportsView(self.content_frame, self.controller))
