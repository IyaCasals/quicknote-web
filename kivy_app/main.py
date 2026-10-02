from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from config import DATABASE_FILENAME
from data_store import PRIORITIES, QuickNoteError, QuickNoteStore


class QuickNoteMobile(App):
    def build(self):
        database_path = Path(self.user_data_dir) / DATABASE_FILENAME
        self.store = QuickNoteStore(database_path)
        self.current_user: dict[str, Any] | None = None
        self.current_view = "dashboard"
        self.categories: list[dict[str, Any]] = []
        self.notes: list[dict[str, Any]] = []
        self.root_box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        self.show_login()
        return self.root_box

    def on_stop(self):
        if hasattr(self, "store"):
            self.store.close()

    @property
    def user_id(self) -> int:
        if not self.current_user:
            raise QuickNoteError("Please log in first.")
        return int(self.current_user["id"])

    def clear(self):
        self.root_box.clear_widgets()

    def toast(self, message: str, title: str = "QuickNote"):
        label = Label(text=message, halign="center", valign="middle")
        label.bind(size=lambda instance, *_: setattr(instance, "text_size", (instance.width - dp(20), None)))
        popup = Popup(title=title, content=label, size_hint=(0.86, 0.32))
        popup.open()

    def field(self, hint: str, password: bool = False, multiline: bool = False, height: int = 46) -> TextInput:
        return TextInput(
            hint_text=hint,
            multiline=multiline,
            password=password,
            size_hint_y=None,
            height=dp(height),
            padding=(dp(10), dp(10)),
        )

    def heading(self, title: str, subtitle: str = "") -> BoxLayout:
        layout = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(64), spacing=dp(2))
        layout.add_widget(Label(text=title, font_size="24sp", bold=True, halign="left", text_size=(dp(320), None)))
        if subtitle:
            layout.add_widget(Label(text=subtitle, font_size="13sp", halign="left", text_size=(dp(320), None)))
        return layout

    def show_login(self):
        self.clear()
        self.root_box.add_widget(Label(text="QuickNote", font_size="32sp", bold=True, size_hint_y=None, height=dp(70)))
        self.root_box.add_widget(Label(text="Python + Kivy + SQLite thesis app", size_hint_y=None, height=dp(32)))
        self.identifier_input = self.field("Username or email")
        self.password_input = self.field("Password", password=True)
        self.root_box.add_widget(self.identifier_input)
        self.root_box.add_widget(self.password_input)
        self.root_box.add_widget(Button(text="Login", size_hint_y=None, height=dp(50), on_press=lambda _: self.login()))
        self.root_box.add_widget(Button(text="Create account", size_hint_y=None, height=dp(50), on_press=lambda _: self.show_register()))

    def show_register(self):
        self.clear()
        self.root_box.add_widget(self.heading("Create Account", "Starter categories are created automatically."))
        self.username_input = self.field("Username")
        self.email_input = self.field("Email")
        self.password_input = self.field("Password", password=True)
        self.root_box.add_widget(self.username_input)
        self.root_box.add_widget(self.email_input)
        self.root_box.add_widget(self.password_input)
        self.root_box.add_widget(Button(text="Register", size_hint_y=None, height=dp(50), on_press=lambda _: self.register()))
        self.root_box.add_widget(Button(text="Back to login", size_hint_y=None, height=dp(50), on_press=lambda _: self.show_login()))

    def register(self):
        try:
            self.store.register(self.username_input.text, self.email_input.text, self.password_input.text)
            self.toast("Account created. You can now log in.")
            self.show_login()
        except QuickNoteError as exc:
            self.toast(str(exc), "Registration failed")

    def login(self):
        try:
            self.current_user = self.store.authenticate(self.identifier_input.text, self.password_input.text)
            self.load_data()
            self.show_dashboard()
        except QuickNoteError as exc:
            self.toast(str(exc), "Login failed")

    def logout(self):
        self.current_user = None
        self.show_login()

    def load_data(self):
        self.categories = self.store.list_categories(self.user_id)
        self.notes = self.store.list_notes(self.user_id)

    def refresh_view(self):
        self.load_data()
        if self.current_view == "dashboard":
            self.show_dashboard()
        elif self.current_view == "notes":
            self.show_notes()
        elif self.current_view == "categories":
            self.show_categories()
        elif self.current_view == "reports":
            self.show_reports()

    def use_shell(self, title: str, subtitle: str = "") -> BoxLayout:
        self.clear()
        self.root_box.add_widget(self.heading(title, subtitle))
        content = BoxLayout(orientation="vertical", spacing=dp(8))
        self.root_box.add_widget(content)
        self.root_box.add_widget(self.bottom_nav())
        return content

    def bottom_nav(self) -> BoxLayout:
        nav = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(5))
        items = [
            ("Home", self.show_dashboard),
            ("Notes", self.show_notes),
            ("+ New", self.open_editor),
            ("Cats", self.show_categories),
            ("Reports", self.show_reports),
        ]
        for label, callback in items:
            nav.add_widget(Button(text=label, on_press=lambda _, cb=callback: cb()))
        return nav

    def scroll_container(self) -> tuple[ScrollView, BoxLayout]:
        list_container = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        list_container.bind(minimum_height=list_container.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(list_container)
        return scroll, list_container

    def show_dashboard(self, *_):
        self.current_view = "dashboard"
        summary = self.store.dashboard(self.user_id)
        content = self.use_shell("Dashboard", f"Welcome, {self.current_user['username']}")
        cards = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(82))
        cards.add_widget(self.metric_card("Notes", summary["total_notes"]))
        cards.add_widget(self.metric_card("Pinned", summary["pinned_notes"]))
        cards.add_widget(self.metric_card("Categories", summary["total_categories"]))
        content.add_widget(cards)

        scroll, list_container = self.scroll_container()
        list_container.add_widget(self.section_label("Recent Notes"))
        if summary["recent_notes"]:
            for note in summary["recent_notes"]:
                list_container.add_widget(self.note_button(note))
        else:
            list_container.add_widget(self.empty_label("No notes yet. Tap + New to create one."))

        list_container.add_widget(self.section_label("Notes by Category"))
        if summary["notes_by_category"]:
            for category, count in summary["notes_by_category"].items():
                list_container.add_widget(self.row_label(f"{category}: {count}"))
        else:
            list_container.add_widget(self.empty_label("No category data yet."))
        content.add_widget(scroll)

    def show_notes(self, *_):
        self.current_view = "notes"
        content = self.use_shell("Notes", "Search, filter, open, and edit notes.")
        filter_row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(46))
        self.search_input = self.field("Search notes", height=46)
        self.search_input.bind(text=lambda *_: self.render_note_list())
        self.priority_filter = Spinner(text="All Priorities", values=["All Priorities"] + PRIORITIES, size_hint_y=None, height=dp(46))
        self.priority_filter.bind(text=lambda *_: self.render_note_list())
        filter_row.add_widget(self.search_input)
        filter_row.add_widget(self.priority_filter)
        content.add_widget(filter_row)

        category_values = ["All Categories"] + [category["name"] for category in self.categories]
        self.category_filter = Spinner(text="All Categories", values=category_values, size_hint_y=None, height=dp(46))
        self.category_filter.bind(text=lambda *_: self.render_note_list())
        content.add_widget(self.category_filter)

        self.notes_scroll, self.notes_container = self.scroll_container()
        content.add_widget(self.notes_scroll)
        self.render_note_list()

    def render_note_list(self):
        self.notes_container.clear_widgets()
        category_id = self.category_id_from_name(self.category_filter.text)
        priority = None if self.priority_filter.text == "All Priorities" else self.priority_filter.text
        notes = self.store.list_notes(self.user_id, self.search_input.text, category_id, priority)
        if not notes:
            self.notes_container.add_widget(self.empty_label("No notes found."))
            return
        for note in notes:
            self.notes_container.add_widget(self.note_button(note))

    def show_categories(self, *_):
        self.current_view = "categories"
        content = self.use_shell("Categories", "Create, rename, or delete note groups.")
        create_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self.category_name_input = self.field("New category", height=46)
        create_row.add_widget(self.category_name_input)
        create_row.add_widget(Button(text="Add", size_hint_x=None, width=dp(90), on_press=lambda _: self.add_category()))
        content.add_widget(create_row)

        scroll, list_container = self.scroll_container()
        if not self.categories:
            list_container.add_widget(self.empty_label("No categories yet."))
        for category in self.categories:
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
            row.add_widget(Label(text=f"{category['name']} ({category['note_count']})", halign="left"))
            row.add_widget(Button(text="Rename", size_hint_x=None, width=dp(92), on_press=partial(self.open_category_editor, category)))
            row.add_widget(Button(text="Delete", size_hint_x=None, width=dp(82), on_press=partial(self.confirm_delete_category, category)))
            list_container.add_widget(row)
        content.add_widget(scroll)

    def add_category(self):
        try:
            self.store.create_category(self.user_id, self.category_name_input.text)
            self.refresh_view()
        except QuickNoteError as exc:
            self.toast(str(exc), "Category failed")

    def open_category_editor(self, category: dict[str, Any], *_):
        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        name_input = self.field("Category name")
        name_input.text = category["name"]
        layout.add_widget(name_input)
        actions = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        popup = Popup(title="Rename Category", content=layout, size_hint=(0.9, 0.36))

        def save(_button):
            try:
                self.store.rename_category(self.user_id, category["id"], name_input.text)
                popup.dismiss()
                self.refresh_view()
            except QuickNoteError as exc:
                self.toast(str(exc), "Rename failed")

        actions.add_widget(Button(text="Save", on_press=save))
        actions.add_widget(Button(text="Cancel", on_press=lambda _: popup.dismiss()))
        layout.add_widget(actions)
        popup.open()

    def confirm_delete_category(self, category: dict[str, Any], *_):
        self.confirm(
            f"Delete category '{category['name']}'?\nExisting notes become Uncategorized.",
            lambda: self.delete_category(category["id"]),
            "Delete Category",
        )

    def delete_category(self, category_id: int):
        try:
            self.store.delete_category(self.user_id, category_id)
            self.refresh_view()
        except QuickNoteError as exc:
            self.toast(str(exc), "Delete failed")

    def show_reports(self, *_):
        self.current_view = "reports"
        summary = self.store.dashboard(self.user_id)
        content = self.use_shell("Reports", "Summary generated from the local SQLite database.")
        content.add_widget(self.metric_card("Total Notes", summary["total_notes"]))
        content.add_widget(self.metric_card("Pinned Notes", summary["pinned_notes"]))
        content.add_widget(self.metric_card("Total Categories", summary["total_categories"]))
        content.add_widget(Button(text="Export PDF Report", size_hint_y=None, height=dp(48), on_press=lambda _: self.export_pdf(summary)))

        scroll, list_container = self.scroll_container()
        list_container.add_widget(self.section_label("Notes per Category"))
        if summary["notes_by_category"]:
            for category, count in summary["notes_by_category"].items():
                list_container.add_widget(self.row_label(f"{category}: {count}"))
        else:
            list_container.add_widget(self.empty_label("No report data yet."))
        content.add_widget(scroll)

    def export_pdf(self, summary: dict[str, Any]):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            report_path = Path(self.user_data_dir) / "quicknote_report.pdf"
            pdf = canvas.Canvas(str(report_path), pagesize=letter)
            width, height = letter
            y = height - 72
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(72, y, "QuickNote Report")
            y -= 36
            pdf.setFont("Helvetica", 12)
            pdf.drawString(72, y, f"User: {self.current_user['username']}")
            y -= 24
            pdf.drawString(72, y, f"Total notes: {summary['total_notes']}")
            y -= 20
            pdf.drawString(72, y, f"Pinned notes: {summary['pinned_notes']}")
            y -= 20
            pdf.drawString(72, y, f"Categories: {summary['total_categories']}")
            y -= 32
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(72, y, "Notes by Category")
            y -= 24
            pdf.setFont("Helvetica", 12)
            for category, count in summary["notes_by_category"].items():
                pdf.drawString(88, y, f"{category}: {count}")
                y -= 18
            pdf.save()
            self.toast(f"PDF saved to:\n{report_path}", "Report exported")
        except Exception as exc:
            self.toast(str(exc), "PDF export failed")

    def open_editor(self, note: dict[str, Any] | None = None, *_):
        container = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        body = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(body)

        title_input = self.field("Title")
        title_input.text = (note or {}).get("title", "")
        content_input = self.field("Content", multiline=True, height=220)
        content_input.text = (note or {}).get("content", "")

        category_values = ["Uncategorized"] + [category["name"] for category in self.categories]
        category_spinner = Spinner(
            text=(note or {}).get("category_name", "Uncategorized"),
            values=category_values,
            size_hint_y=None,
            height=dp(46),
        )
        priority_spinner = Spinner(
            text=(note or {}).get("priority", "Normal"),
            values=PRIORITIES,
            size_hint_y=None,
            height=dp(46),
        )
        pinned_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        pinned_box = CheckBox(active=bool((note or {}).get("is_pinned")), size_hint_x=None, width=dp(44))
        pinned_row.add_widget(Label(text="Pinned", halign="left"))
        pinned_row.add_widget(pinned_box)

        body.add_widget(title_input)
        body.add_widget(content_input)
        body.add_widget(category_spinner)
        body.add_widget(priority_spinner)
        body.add_widget(pinned_row)
        if note:
            body.add_widget(self.row_label(f"Created: {note['created_at']}"))
            body.add_widget(self.row_label(f"Updated: {note['updated_at']}"))

        actions = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        popup = Popup(title="Edit Note" if note else "New Note", content=container, size_hint=(0.94, 0.9))

        def save_note(_button):
            try:
                payload = {
                    "title": title_input.text,
                    "content": content_input.text,
                    "category_id": self.category_id_from_name(category_spinner.text),
                    "priority": priority_spinner.text,
                    "is_pinned": pinned_box.active,
                }
                if note:
                    self.store.update_note(self.user_id, note["id"], payload)
                else:
                    self.store.create_note(self.user_id, payload)
                popup.dismiss()
                self.refresh_view()
            except QuickNoteError as exc:
                self.toast(str(exc), "Save failed")

        actions.add_widget(Button(text="Save", on_press=save_note))
        if note:
            actions.add_widget(Button(text="Delete", on_press=lambda _: self.confirm_delete_note(note, popup)))
        actions.add_widget(Button(text="Cancel", on_press=lambda _: popup.dismiss()))
        container.add_widget(scroll)
        container.add_widget(actions)
        popup.open()

    def confirm_delete_note(self, note: dict[str, Any], editor_popup: Popup):
        def delete():
            try:
                self.store.delete_note(self.user_id, note["id"])
                editor_popup.dismiss()
                self.refresh_view()
            except QuickNoteError as exc:
                self.toast(str(exc), "Delete failed")

        self.confirm(f"Delete note '{note['title']}' permanently?", delete, "Delete Note")

    def confirm(self, message: str, callback, title: str):
        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        label = Label(text=message, halign="center", valign="middle")
        label.bind(size=lambda instance, *_: setattr(instance, "text_size", (instance.width - dp(20), None)))
        layout.add_widget(label)
        actions = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        popup = Popup(title=title, content=layout, size_hint=(0.9, 0.36))

        def proceed(_button):
            popup.dismiss()
            callback()

        actions.add_widget(Button(text="Yes", on_press=proceed))
        actions.add_widget(Button(text="No", on_press=lambda _: popup.dismiss()))
        layout.add_widget(actions)
        popup.open()

    def note_button(self, note: dict[str, Any]) -> Button:
        prefix = "[PIN] " if note["is_pinned"] else ""
        button = Button(
            text=f"{prefix}{note['title']}\n{note['category_name']} | {note['priority']} | {note['updated_at']}",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(72),
        )
        button.bind(size=lambda instance, *_: setattr(instance, "text_size", (instance.width - dp(20), None)))
        button.bind(on_press=partial(self.open_editor, note))
        return button

    def category_id_from_name(self, name: str) -> int | None:
        if name in ("Uncategorized", "All Categories"):
            return None
        for category in self.categories:
            if category["name"] == name:
                return int(category["id"])
        return None

    def metric_card(self, label: str, value: int) -> BoxLayout:
        card = BoxLayout(orientation="vertical", padding=dp(8), size_hint_y=None, height=dp(76))
        card.add_widget(Label(text=label, font_size="13sp"))
        card.add_widget(Label(text=str(value), font_size="24sp", bold=True))
        return card

    def section_label(self, text: str) -> Label:
        return Label(text=text, bold=True, font_size="18sp", size_hint_y=None, height=dp(38), halign="left")

    def row_label(self, text: str) -> Label:
        label = Label(text=text, size_hint_y=None, height=dp(34), halign="left", valign="middle")
        label.bind(size=lambda instance, *_: setattr(instance, "text_size", (instance.width - dp(20), None)))
        return label

    def empty_label(self, text: str) -> Label:
        label = Label(text=text, size_hint_y=None, height=dp(48), halign="center", valign="middle")
        label.bind(size=lambda instance, *_: setattr(instance, "text_size", (instance.width - dp(20), None)))
        return label


if __name__ == "__main__":
    QuickNoteMobile().run()
