import customtkinter as ctk

from desktop_app.views.base_view import BaseView


class DashboardView(BaseView):
    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)
        summary = self.controller.report_generator.summary(self.controller.user_id)

        ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 14)
        )
        cards = [
            ("Total Notes", summary["total_notes"]),
            ("Pinned Notes", summary["pinned_notes"]),
            ("Categories", summary["total_categories"]),
        ]
        for col, (label, value) in enumerate(cards):
            card = ctk.CTkFrame(self, corner_radius=8)
            card.grid(row=1, column=col, padx=(0 if col == 0 else 10, 0), pady=(0, 18), sticky="ew")
            ctk.CTkLabel(card, text=label).pack(anchor="w", padx=18, pady=(16, 2))
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=18, pady=(0, 16))

        left = ctk.CTkFrame(self, corner_radius=8)
        left.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(0, 10))
        right = ctk.CTkFrame(self, corner_radius=8)
        right.grid(row=2, column=2, sticky="nsew")

        ctk.CTkLabel(left, text="Recent Notes", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(14, 8))
        notes = self.controller.note_manager.list_for_user(self.controller.user_id, limit=6)
        if not notes:
            ctk.CTkLabel(left, text="No notes yet. Create your first note.").pack(anchor="w", padx=16, pady=10)
        for note in notes:
            text = f"{'Pinned - ' if note.is_pinned else ''}{note.title}  |  {note.priority}"
            ctk.CTkButton(left, text=text, anchor="w", fg_color="transparent", command=lambda note_id=note.id: self.controller.shell.show_editor(note_id)).pack(
                fill="x", padx=12, pady=4
            )

        ctk.CTkLabel(right, text="Notes by Category", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(14, 8))
        if not summary["notes_by_category"]:
            ctk.CTkLabel(right, text="No category activity yet.").pack(anchor="w", padx=16, pady=10)
        for name, count in summary["notes_by_category"].items():
            ctk.CTkLabel(right, text=f"{name}: {count}").pack(anchor="w", padx=16, pady=4)
