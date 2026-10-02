from __future__ import annotations

from functools import partial

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from supabase_client import QuickNoteApiError, SupabaseClient


PRIORITIES = ["Low", "Normal", "High"]


class QuickNoteMobile(App):
    def build(self):
        self.api = SupabaseClient()
        self.notes = []
        self.categories = []
        self.root_box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        self.show_login()
        return self.root_box

    def clear(self):
        self.root_box.clear_widgets()

    def toast(self, message: str, title: str = "QuickNote"):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.86, 0.32))
        popup.open()

    def field(self, hint: str, password: bool = False) -> TextInput:
        return TextInput(hint_text=hint, multiline=False, password=password, size_hint_y=None, height=dp(46))

    def show_login(self):
        self.clear()
        self.root_box.add_widget(Label(text="QuickNote", font_size="30sp", bold=True, size_hint_y=None, height=dp(54)))
        self.identifier_input = self.field("Username or email")
        self.password_input = self.field("Password", password=True)
        self.root_box.add_widget(self.identifier_input)
        self.root_box.add_widget(self.password_input)
        self.root_box.add_widget(Button(text="Login", size_hint_y=None, height=dp(48), on_press=lambda _: self.login()))
        self.root_box.add_widget(Button(text="Create account", size_hint_y=None, height=dp(48), on_press=lambda _: self.show_register()))

    def show_register(self):
        self.clear()
        self.root_box.add_widget(Label(text="Create Account", font_size="26sp", bold=True, size_hint_y=None, height=dp(54)))
        self.username_input = self.field("Username")
        self.email_input = self.field("Email")
        self.password_input = self.field("Password", password=True)
        self.root_box.add_widget(self.username_input)
        self.root_box.add_widget(self.email_input)
        self.root_box.add_widget(self.password_input)
        self.root_box.add_widget(Button(text="Register", size_hint_y=None, height=dp(48), on_press=lambda _: self.register()))
        self.root_box.add_widget(Button(text="Back to login", size_hint_y=None, height=dp(48), on_press=lambda _: self.show_login()))

    def register(self):
        try:
            self.api.register(self.username_input.text, self.email_input.text, self.password_input.text)
            self.toast("Account created. You can now log in.")
            self.show_login()
        except QuickNoteApiError as exc:
            self.toast(str(exc), "Registration failed")

    def login(self):
        try:
            self.api.login(self.identifier_input.text, self.password_input.text)
            self.load_data()
            self.show_notes()
        except QuickNoteApiError as exc:
            self.toast(str(exc), "Login failed")

    def load_data(self):
        self.categories = self.api.list_categories()
        self.notes = self.api.list_notes()

    def show_notes(self):
        self.clear()
        header = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        header.add_widget(Label(text="Notes", font_size="24sp", bold=True))
        header.add_widget(Button(text="+ New", size_hint_x=None, width=dp(96), on_press=lambda _: self.open_editor()))
        self.root_box.add_widget(header)

        self.search_input = self.field("Search notes")
        self.search_input.bind(text=lambda *_: self.render_note_list())
        self.root_box.add_widget(self.search_input)

        self.list_container = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.list_container.bind(minimum_height=self.list_container.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.list_container)
        self.root_box.add_widget(scroll)

        footer = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        footer.add_widget(Button(text="Refresh", on_press=lambda _: self.refresh()))
        footer.add_widget(Button(text="Logout", on_press=lambda _: self.logout()))
        self.root_box.add_widget(footer)
        self.render_note_list()

    def refresh(self):
        try:
            self.load_data()
            self.render_note_list()
        except QuickNoteApiError as exc:
            self.toast(str(exc), "Refresh failed")

    def logout(self):
        self.api.logout()
        self.show_login()

    def render_note_list(self):
        self.list_container.clear_widgets()
        query = (self.search_input.text or "").lower().strip()
        visible = []
        for note in self.notes:
            category_name = (note.get("categories") or {}).get("name", "Uncategorized")
            haystack = f"{note.get('title', '')} {note.get('content', '')} {category_name}".lower()
            if not query or query in haystack:
                visible.append(note)

        if not visible:
            self.list_container.add_widget(Label(text="No notes found.", size_hint_y=None, height=dp(42)))
            return

        for note in visible:
            category_name = (note.get("categories") or {}).get("name", "Uncategorized")
            prefix = "Pinned - " if note.get("is_pinned") else ""
            button = Button(
                text=f"{prefix}{note['title']}\n{category_name} | {note['priority']}",
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(68),
            )
            button.bind(size=lambda instance, *_: setattr(instance, "text_size", (instance.width - dp(20), None)))
            button.bind(on_press=partial(self.open_editor, note))
            self.list_container.add_widget(button)

    def open_editor(self, note=None, *_):
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        title_input = TextInput(text=(note or {}).get("title", ""), hint_text="Title", multiline=False, size_hint_y=None, height=dp(44))
        content_input = TextInput(text=(note or {}).get("content", ""), hint_text="Content", size_hint_y=None, height=dp(150))

        category_values = ["Uncategorized"] + [category["name"] for category in self.categories]
        category_spinner = Spinner(text="Uncategorized", values=category_values, size_hint_y=None, height=dp(44))
        if note and note.get("categories"):
            category_spinner.text = note["categories"]["name"]

        priority_spinner = Spinner(text=(note or {}).get("priority", "Normal"), values=PRIORITIES, size_hint_y=None, height=dp(44))

        pinned_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        pinned_box = CheckBox(active=bool((note or {}).get("is_pinned")), size_hint_x=None, width=dp(44))
        pinned_row.add_widget(Label(text="Pinned"))
        pinned_row.add_widget(pinned_box)

        layout.add_widget(title_input)
        layout.add_widget(content_input)
        layout.add_widget(category_spinner)
        layout.add_widget(priority_spinner)
        layout.add_widget(pinned_row)

        actions = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        popup = Popup(title="Edit Note" if note else "New Note", content=layout, size_hint=(0.94, 0.88))

        def save_note(_button):
            try:
                title = title_input.text.strip()
                if not title:
                    raise QuickNoteApiError("Title is required.")
                category_id = None
                for category in self.categories:
                    if category["name"] == category_spinner.text:
                        category_id = category["id"]
                        break
                payload = {
                    "title": title,
                    "content": content_input.text.strip(),
                    "category_id": category_id,
                    "priority": priority_spinner.text,
                    "is_pinned": pinned_box.active,
                }
                if note:
                    self.api.update_note(note["id"], payload)
                else:
                    self.api.create_note(payload)
                popup.dismiss()
                self.load_data()
                self.render_note_list()
            except QuickNoteApiError as exc:
                self.toast(str(exc), "Save failed")

        actions.add_widget(Button(text="Save", on_press=save_note))
        if note:
            def delete_note(_button):
                try:
                    self.api.delete_note(note["id"])
                    popup.dismiss()
                    self.load_data()
                    self.render_note_list()
                except QuickNoteApiError as exc:
                    self.toast(str(exc), "Delete failed")

            actions.add_widget(Button(text="Delete", on_press=delete_note))
        actions.add_widget(Button(text="Cancel", on_press=lambda _: popup.dismiss()))
        layout.add_widget(actions)
        popup.open()


if __name__ == "__main__":
    QuickNoteMobile().run()
