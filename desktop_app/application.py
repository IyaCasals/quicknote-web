import customtkinter as ctk

from desktop_app.database import SessionLocal
from desktop_app.services import AuthService, CategoryManager, NoteManager, ReportGenerator, SearchManager
from desktop_app.views.auth_views import LoginView, RegisterView
from desktop_app.views.shell_view import ShellView


class QuickNoteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("QuickNote")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.session = SessionLocal()
        self.auth_service = AuthService(self.session)
        self.note_manager = NoteManager(self.session)
        self.category_manager = CategoryManager(self.session)
        self.search_manager = SearchManager(self.session)
        self.report_generator = ReportGenerator(self.session)
        self.current_user = None
        self.shell: ShellView | None = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.show_login()

    @property
    def user_id(self) -> int:
        return self.current_user.id

    def _swap_root(self, view) -> None:
        for child in self.winfo_children():
            child.destroy()
        view.grid(row=0, column=0, sticky="nsew")
        view.render()

    def show_login(self) -> None:
        self.shell = None
        self._swap_root(LoginView(self, self))

    def show_register(self) -> None:
        self._swap_root(RegisterView(self, self))

    def register(self, username: str, email: str, password: str, confirm_password: str) -> None:
        self.current_user = self.auth_service.register(username, email, password, confirm_password)
        self.show_shell()

    def login(self, identifier: str, password: str) -> None:
        self.current_user = self.auth_service.login(identifier, password)
        self.show_shell()

    def show_shell(self) -> None:
        self.shell = ShellView(self, self)
        self._swap_root(self.shell)

    def logout(self) -> None:
        self.current_user = None
        self.show_login()

    def show_message(self, message: str, error: bool = False) -> None:
        if self.shell:
            self.shell.set_message(message, error)

    def _close(self) -> None:
        self.session.close()
        self.destroy()
