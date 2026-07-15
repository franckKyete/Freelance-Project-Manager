"""Reports screen — financial and productivity report generation."""

import tkinter as tk
from tkinter import ttk, messagebox

from src.services.report_service import ReportService
from src.gui.theme import (
    BG_DARK, BG_CARD, BG_PANEL, ACCENT, ACCENT_2, SUCCESS,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED,
    FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
    CONTENT_PAD, CARD_PAD,
)
from src.gui.widgets import make_button, make_scrolled_tree, section_title


REPORT_TYPES = [
    ("💰  Income", "income"),
    ("💸  Expenses", "expense"),
    ("⏱  Productivity", "productivity"),
    ("📈  Profit", "profit"),
]


class ReportsFrame(tk.Frame):
    """Reports screen for generating financial and productivity summaries."""

    def __init__(self, parent: tk.Frame) -> None:
        super().__init__(parent, bg=BG_DARK)
        self._svc = ReportService()
        self._build_ui()

    def _build_ui(self) -> None:
        self.pack(fill=tk.BOTH, expand=True, padx=CONTENT_PAD, pady=CONTENT_PAD)

        section_title(self, "📊  Reports").pack(anchor="w", pady=(0, 16))

        # Two-column layout: report type buttons (left) + output (right)
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # ── Left: report selector ─────────────────────────────────────
        selector = tk.Frame(main, bg=BG_PANEL, width=200, padx=12, pady=16)
        selector.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        selector.grid_propagate(False)

        tk.Label(selector, text="Report Type", font=FONT_H3,
                 bg=BG_PANEL, fg=FG_SECONDARY).pack(anchor="w", pady=(0, 12))

        for label, key in REPORT_TYPES:
            btn = make_button(selector, label, lambda k=key: self._generate(k))
            btn.pack(fill=tk.X, pady=3)

        # ── Right: output area ────────────────────────────────────────
        self._output = tk.Frame(main, bg=BG_DARK)
        self._output.grid(row=0, column=1, sticky="nsew")

        self._show_prompt()

    def _show_prompt(self) -> None:
        for w in self._output.winfo_children():
            w.destroy()
        tk.Label(self._output,
                 text="Select a report type to generate →",
                 font=FONT_BODY, bg=BG_DARK, fg=FG_MUTED).pack(expand=True)

    def _generate(self, report_key: str) -> None:
        for w in self._output.winfo_children():
            w.destroy()
        try:
            data = getattr(self._svc, f"{report_key}_report")()
            self._render_report(data)
        except Exception as exc:
            messagebox.showerror("Report Error", str(exc), parent=self)

    def _render_report(self, data: dict) -> None:
        """Render a report dictionary as a title + summary + table."""
        frame = tk.Frame(self._output, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(frame, text=data["title"], font=FONT_H2,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 8))

        # Summary cards
        summaries = {k: v for k, v in data.items()
                     if k not in ("title", "rows", "columns", "by_category")}
        if summaries:
            summary_row = tk.Frame(frame, bg=BG_DARK)
            summary_row.pack(fill=tk.X, pady=(0, 12))
            for key, value in summaries.items():
                card = tk.Frame(summary_row, bg=BG_CARD, padx=14, pady=10)
                card.pack(side=tk.LEFT, padx=(0, 10))
                tk.Label(card, text=key.replace("_", " ").title(),
                         font=FONT_SMALL, bg=BG_CARD, fg=FG_SECONDARY).pack(anchor="w")
                tk.Label(card, text=str(value), font=FONT_H3,
                         bg=BG_CARD, fg=ACCENT_2).pack(anchor="w")

        # Category breakdown (expenses only)
        by_cat = data.get("by_category", {})
        if by_cat:
            tk.Label(frame, text="By Category", font=FONT_H3,
                     bg=BG_DARK, fg=FG_SECONDARY).pack(anchor="w", pady=(8, 4))
            for cat, amount in by_cat.items():
                row = tk.Frame(frame, bg=BG_DARK)
                row.pack(fill=tk.X)
                tk.Label(row, text=cat, font=FONT_SMALL, bg=BG_DARK, fg=FG_SECONDARY,
                         width=20, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=amount, font=FONT_BODY, bg=BG_DARK, fg=FG_PRIMARY
                         ).pack(side=tk.LEFT)

        # Table
        rows = data.get("rows", [])
        columns = data.get("columns", [])
        if columns and rows:
            tk.Label(frame, text="Detail", font=FONT_H3,
                     bg=BG_DARK, fg=FG_SECONDARY).pack(anchor="w", pady=(12, 4))
            tree_frame, tree = make_scrolled_tree(frame, columns, heights=14)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            for col in columns:
                tree.column(col, minwidth=80)
            for row in rows:
                tree.insert("", tk.END, values=[row.get(c, "") for c in columns])
        elif not rows:
            tk.Label(frame, text="No data to display.", font=FONT_BODY,
                     bg=BG_DARK, fg=FG_MUTED).pack(anchor="w", pady=16)

    def refresh(self) -> None:
        """Reset the output area."""
        self._show_prompt()
