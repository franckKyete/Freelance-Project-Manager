"""Dashboard screen — landing page shown after login."""

import tkinter as tk
from tkinter import ttk

from src.services.project_service import ProjectService
from src.services.invoice_service import InvoiceService
from src.repositories.time_entry_repository import TimeEntryRepository
from src.models.person import Freelancer
from src.utils.validators import format_currency, format_hours
from src.gui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, ACCENT, ACCENT_2,
    SUCCESS, WARNING, DANGER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
    CONTENT_PAD, CARD_PAD,
)
from src.gui.widgets import section_title


class DashboardFrame(tk.Frame):
    """Main dashboard displaying key metrics and recent activity.

    Args:
        parent: The content area frame managed by AppWindow.
        freelancer: The logged-in Freelancer instance.
    """

    def __init__(self, parent: tk.Frame, freelancer: Freelancer) -> None:
        super().__init__(parent, bg=BG_DARK)
        self._freelancer = freelancer
        self._project_svc = ProjectService()
        self._invoice_svc = InvoiceService()
        self._time_repo = TimeEntryRepository()
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct all dashboard widgets."""
        self.pack(fill=tk.BOTH, expand=True, padx=CONTENT_PAD, pady=CONTENT_PAD)

        # ── Header ────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header,
                 text=f"Welcome back, {self._freelancer.full_name.split()[0]} 👋",
                 font=FONT_H1, bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w")
        tk.Label(header,
                 text="Here's a snapshot of your freelance business today.",
                 font=FONT_BODY, bg=BG_DARK, fg=FG_SECONDARY).pack(anchor="w")

        # ── Stats Grid ────────────────────────────────────────────────
        stats_frame = tk.Frame(self, bg=BG_DARK)
        stats_frame.pack(fill=tk.X, pady=(0, 24))

        # Gather data
        active_projects = self._project_svc.get_active_projects()
        total_income = self._invoice_svc.get_total_income()
        pending_invoices = self._invoice_svc.get_pending()
        weekly_hours = self._time_repo.total_hours_this_week()

        cards = [
            ("🗂  Active Projects", str(len(active_projects)), ACCENT, "ongoing work"),
            ("💰  Total Income", format_currency(total_income), ACCENT_2, "from paid invoices"),
            ("📄  Pending Invoices", str(len(pending_invoices)), WARNING, "awaiting payment"),
            ("⏱  Weekly Hours", format_hours(weekly_hours), SUCCESS, "logged this week"),
        ]

        for i, (title, value, color, sub) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=BG_CARD, padx=CARD_PAD, pady=CARD_PAD)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)

            # Coloured accent strip
            strip = tk.Frame(card, bg=color, height=3)
            strip.pack(fill=tk.X, pady=(0, 10))

            tk.Label(card, text=title, font=FONT_SMALL,
                     bg=BG_CARD, fg=FG_SECONDARY).pack(anchor="w")
            tk.Label(card, text=value, font=FONT_H2,
                     bg=BG_CARD, fg=FG_PRIMARY).pack(anchor="w", pady=(4, 0))
            tk.Label(card, text=sub, font=FONT_SMALL,
                     bg=BG_CARD, fg=FG_MUTED).pack(anchor="w")

        # ── Recent Activity ────────────────────────────────────────────
        bottom = tk.Frame(self, bg=BG_DARK)
        bottom.pack(fill=tk.BOTH, expand=True)
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=2)

        # Active projects list
        proj_card = tk.Frame(bottom, bg=BG_CARD, padx=CARD_PAD, pady=CARD_PAD)
        proj_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        tk.Label(proj_card, text="Active Projects", font=FONT_H3,
                 bg=BG_CARD, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 8))

        for proj in active_projects[:8]:
            row = tk.Frame(proj_card, bg=BG_CARD)
            row.pack(fill=tk.X, pady=3)
            progress = proj.calculate_progress()
            tk.Label(row, text=proj.title, font=FONT_BODY,
                     bg=BG_CARD, fg=FG_PRIMARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            pct = tk.Label(row, text=f"{progress*100:.0f}%",
                           font=FONT_SMALL, bg=BG_CARD, fg=ACCENT)
            pct.pack(side=tk.RIGHT)

        if not active_projects:
            tk.Label(proj_card, text="No active projects yet.", font=FONT_BODY,
                     bg=BG_CARD, fg=FG_MUTED).pack(anchor="w")

        # Pending invoices list
        inv_card = tk.Frame(bottom, bg=BG_CARD, padx=CARD_PAD, pady=CARD_PAD)
        inv_card.grid(row=0, column=1, sticky="nsew")
        tk.Label(inv_card, text="Pending Invoices", font=FONT_H3,
                 bg=BG_CARD, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 8))

        for inv in pending_invoices[:8]:
            row = tk.Frame(inv_card, bg=BG_CARD)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=inv.invoice_number, font=FONT_SMALL,
                     bg=BG_CARD, fg=FG_SECONDARY).pack(side=tk.LEFT)
            tk.Label(row, text=format_currency(inv.amount), font=FONT_SMALL,
                     bg=BG_CARD, fg=WARNING).pack(side=tk.RIGHT)

        if not pending_invoices:
            tk.Label(inv_card, text="No pending invoices. 🎉", font=FONT_BODY,
                     bg=BG_CARD, fg=FG_MUTED).pack(anchor="w")

    def refresh(self) -> None:
        """Reload dashboard data and redraw widgets."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
