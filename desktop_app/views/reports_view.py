import customtkinter as ctk

from desktop_app.views.base_view import BaseView


class ReportsView(BaseView):
    def render(self) -> None:
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        summary = self.controller.report_generator.summary(self.controller.user_id)
        ctk.CTkLabel(self, text="Reports", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 14)
        )
        stats = ctk.CTkFrame(self, corner_radius=8)
        stats.grid(row=1, column=0, sticky="ew")
        rows = [
            ("Total notes", summary["total_notes"]),
            ("Pinned notes", summary["pinned_notes"]),
            ("Total categories", summary["total_categories"]),
        ]
        for row, (label, value) in enumerate(rows):
            ctk.CTkLabel(stats, text=label, font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, padx=16, pady=10, sticky="w")
            ctk.CTkLabel(stats, text=str(value)).grid(row=row, column=1, padx=16, pady=10, sticky="e")

        by_category = ctk.CTkFrame(self, corner_radius=8)
        by_category.grid(row=2, column=0, sticky="ew", pady=16)
        ctk.CTkLabel(by_category, text="Notes per category", font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w", padx=16, pady=(14, 8)
        )
        if not summary["notes_by_category"]:
            ctk.CTkLabel(by_category, text="No notes to report yet.").pack(anchor="w", padx=16, pady=(0, 14))
        for name, count in summary["notes_by_category"].items():
            ctk.CTkLabel(by_category, text=f"{name}: {count}").pack(anchor="w", padx=16, pady=4)
