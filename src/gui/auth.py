"""First-run authentication / profile setup dialog.

Shown on the very first launch. Creates the freelancer profile that is
stored persistently in the database.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.models.person import Freelancer
from src.repositories.freelancer_repository import FreelancerRepository
from src.gui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, ACCENT, ACCENT_HOVER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL,
)


class AuthScreen(tk.Toplevel):
    """Profile setup dialog displayed on first run.

    Collects the freelancer's personal and professional details,
    validates them, and saves the profile via FreelancerRepository.

    The calling code should check `auth.profile` after the dialog closes:
        auth = AuthScreen(parent)
        parent.wait_window(auth)
        if auth.profile is None:
            # User cancelled — exit app
    """

    def __init__(self, parent: tk.Tk) -> None:
        """Initialise the setup dialog.

        Args:
            parent: The root Tk window.
        """
        super().__init__(parent)
        self.parent = parent
        self.profile: Freelancer | None = None  # Set on successful save
        self._repo = FreelancerRepository()

        self.title("Welcome — Freelance Project Manager")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.grab_set()  # Modal

        # Centre on screen
        self.update_idletasks()
        w, h = 520, 580
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Build all widgets."""
        # Header
        header = tk.Frame(self, bg=ACCENT, height=6)
        header.pack(fill=tk.X)

        body = tk.Frame(self, bg=BG_DARK, padx=40, pady=30)
        body.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(body, text="👋  Welcome!", font=FONT_H1,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w")
        tk.Label(body,
                 text="Let's set up your freelancer profile. You can update it later in Settings.",
                 font=FONT_BODY, bg=BG_DARK, fg=FG_SECONDARY, wraplength=440, justify="left"
                 ).pack(anchor="w", pady=(4, 24))

        # Form
        form = tk.Frame(body, bg=BG_DARK)
        form.pack(fill=tk.X)

        self._entries: dict[str, tk.StringVar] = {}

        fields = [
            ("Full Name *", "full_name", "e.g. Alice Dupont"),
            ("Email *", "email", "e.g. alice@example.com"),
            ("Phone", "phone", "e.g. +32 498 12 34 56"),
            ("Profession", "profession", "e.g. Full-Stack Developer"),
            ("Default Hourly Rate ($)", "hourly_rate", "e.g. 75.00"),
            ("Tax / VAT Number", "tax_number", "e.g. BE0123456789"),
        ]

        for label_text, key, placeholder in fields:
            row = tk.Frame(form, bg=BG_DARK)
            row.pack(fill=tk.X, pady=5)

            tk.Label(row, text=label_text, font=FONT_SMALL,
                     bg=BG_DARK, fg=FG_SECONDARY, anchor="w", width=28
                     ).pack(side=tk.LEFT)

            var = tk.StringVar()
            self._entries[key] = var

            entry = tk.Entry(row, textvariable=var, font=FONT_BODY,
                             bg=BG_CARD, fg=FG_PRIMARY, insertbackground=FG_PRIMARY,
                             relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=BORDER, highlightcolor=ACCENT)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(8, 0))

            # Show placeholder hint
            if placeholder:
                entry.insert(0, placeholder)
                entry.config(fg=FG_MUTED)
                entry.bind("<FocusIn>",
                           lambda e, en=entry, ph=placeholder: self._clear_placeholder(e, en, ph))
                entry.bind("<FocusOut>",
                           lambda e, en=entry, v=var, ph=placeholder: self._restore_placeholder(e, en, v, ph))

        # Save button
        btn_frame = tk.Frame(body, bg=BG_DARK)
        btn_frame.pack(fill=tk.X, pady=(24, 0))

        save_btn = tk.Button(
            btn_frame, text="Create Profile  →",
            font=FONT_H3, bg=ACCENT, fg=FG_PRIMARY,
            activebackground=ACCENT_HOVER, activeforeground=FG_PRIMARY,
            relief="flat", cursor="hand2", pady=10,
            command=self._save_profile,
        )
        save_btn.pack(fill=tk.X)

        # Hover effect
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=ACCENT_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=ACCENT))

        tk.Label(body, text="* Required fields", font=FONT_SMALL,
                 bg=BG_DARK, fg=FG_MUTED).pack(anchor="e", pady=(8, 0))

    # ------------------------------------------------------------------ #
    # Placeholder helpers
    # ------------------------------------------------------------------ #

    def _clear_placeholder(self, event, entry: tk.Entry, placeholder: str) -> None:
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=FG_PRIMARY)

    def _restore_placeholder(self, event, entry: tk.Entry, var: tk.StringVar, placeholder: str) -> None:
        if not var.get():
            entry.insert(0, placeholder)
            entry.config(fg=FG_MUTED)

    def _get_value(self, key: str, placeholder: str = "") -> str:
        """Return the real value of a field, ignoring placeholder text."""
        val = self._entries[key].get().strip()
        # Detect if the field still shows the placeholder
        placeholders = {
            "full_name": "e.g. Alice Dupont",
            "email": "e.g. alice@example.com",
            "phone": "e.g. +32 498 12 34 56",
            "profession": "e.g. Full-Stack Developer",
            "hourly_rate": "e.g. 75.00",
            "tax_number": "e.g. BE0123456789",
        }
        if val == placeholders.get(key, ""):
            return ""
        return val

    # ------------------------------------------------------------------ #
    # Save logic
    # ------------------------------------------------------------------ #

    def _save_profile(self) -> None:
        """Validate inputs and save the freelancer profile."""
        name = self._get_value("full_name")
        email = self._get_value("email")
        phone = self._get_value("phone")
        profession = self._get_value("profession")
        rate_str = self._get_value("hourly_rate")
        tax = self._get_value("tax_number")

        # Validation
        if not name:
            messagebox.showwarning("Validation", "Full Name is required.", parent=self)
            return
        if not email:
            messagebox.showwarning("Validation", "Email is required.", parent=self)
            return

        try:
            hourly_rate = float(rate_str) if rate_str else 0.0
            if hourly_rate < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation",
                                   "Hourly rate must be a valid non-negative number.", parent=self)
            return

        try:
            freelancer = Freelancer(
                full_name=name,
                email=email,
                phone=phone,
                profession=profession,
                hourly_rate=hourly_rate,
                tax_number=tax,
            )
            self._repo.save(freelancer)
            self.profile = freelancer
            self.destroy()
        except ValueError as exc:
            messagebox.showerror("Invalid Data", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not save profile:\n{exc}", parent=self)
