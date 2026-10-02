import customtkinter as ctk

from desktop_app.services.exceptions import QuickNoteError
from desktop_app.views.base_view import BaseView


class LoginView(BaseView):
    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(self, corner_radius=8)
        panel.grid(row=0, column=0, padx=32, pady=32)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="QuickNote", font=ctk.CTkFont(size=32, weight="bold")).grid(
            row=0, column=0, padx=36, pady=(32, 8), sticky="ew"
        )
        ctk.CTkLabel(panel, text="Sign in to your notes").grid(row=1, column=0, padx=36, pady=(0, 24))

        self.identifier_entry = ctk.CTkEntry(panel, width=320, placeholder_text="Username or email")
        self.identifier_entry.grid(row=2, column=0, padx=36, pady=8)
        self.password_entry = ctk.CTkEntry(panel, width=320, placeholder_text="Password", show="*")
        self.password_entry.grid(row=3, column=0, padx=36, pady=8)
        self.status_label = ctk.CTkLabel(panel, text="", text_color="#b42318")
        self.status_label.grid(row=4, column=0, padx=36, pady=(4, 0))

        ctk.CTkButton(panel, text="Login", command=self._login).grid(row=5, column=0, padx=36, pady=(16, 8), sticky="ew")
        ctk.CTkButton(panel, text="Create account", fg_color="transparent", command=self.controller.show_register).grid(
            row=6, column=0, padx=36, pady=(0, 32), sticky="ew"
        )
        self.password_entry.bind("<Return>", lambda _event: self._login())

    def _login(self) -> None:
        try:
            self.controller.login(self.identifier_entry.get(), self.password_entry.get())
        except QuickNoteError as exc:
            self.status_label.configure(text=str(exc))
        except ValueError as exc:
            self.status_label.configure(text=str(exc))


class RegisterView(BaseView):
    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(self, corner_radius=8)
        panel.grid(row=0, column=0, padx=32, pady=32)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Create Account", font=ctk.CTkFont(size=28, weight="bold")).grid(
            row=0, column=0, padx=36, pady=(32, 20), sticky="ew"
        )
        self.username_entry = ctk.CTkEntry(panel, width=320, placeholder_text="Username")
        self.username_entry.grid(row=1, column=0, padx=36, pady=7)
        self.email_entry = ctk.CTkEntry(panel, width=320, placeholder_text="Email")
        self.email_entry.grid(row=2, column=0, padx=36, pady=7)
        self.password_entry = ctk.CTkEntry(panel, width=320, placeholder_text="Password", show="*")
        self.password_entry.grid(row=3, column=0, padx=36, pady=7)
        self.confirm_entry = ctk.CTkEntry(panel, width=320, placeholder_text="Confirm password", show="*")
        self.confirm_entry.grid(row=4, column=0, padx=36, pady=7)
        self.status_label = ctk.CTkLabel(panel, text="", text_color="#b42318")
        self.status_label.grid(row=5, column=0, padx=36, pady=(4, 0))

        ctk.CTkButton(panel, text="Register", command=self._register).grid(
            row=6, column=0, padx=36, pady=(16, 8), sticky="ew"
        )
        ctk.CTkButton(panel, text="Back to login", fg_color="transparent", command=self.controller.show_login).grid(
            row=7, column=0, padx=36, pady=(0, 32), sticky="ew"
        )

    def _register(self) -> None:
        try:
            self.controller.register(
                self.username_entry.get(),
                self.email_entry.get(),
                self.password_entry.get(),
                self.confirm_entry.get(),
            )
        except (QuickNoteError, ValueError) as exc:
            self.status_label.configure(text=str(exc))
