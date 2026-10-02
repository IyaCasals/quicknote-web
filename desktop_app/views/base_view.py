import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller

    def render(self) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        for child in self.winfo_children():
            child.destroy()

    def show_error(self, message: str) -> None:
        self.controller.show_message(message, error=True)

    def show_success(self, message: str) -> None:
        self.controller.show_message(message, error=False)
