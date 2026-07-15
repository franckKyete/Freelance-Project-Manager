"""Main application window with sidebar navigation.

AppWindow is the root Tk window that hosts the persistent sidebar and
the swappable content area. It handles routing between the 6 screens.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.models.person import Freelancer
from src.repositories.freelancer_repository import FreelancerRepository
from src.gui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, ACCENT, ACCENT_HOVER,
    FG_PRIMARY, FG_SECONDARY, FG_MUTED, BORDER,
    FONT_H3, FONT_BODY, FONT_SMALL,
    SIDEBAR_W,
)

# Lazy imports to avoid circular dependency
NAV_ITEMS = [
    ("🏠", "Dashboard",  "dashboard"),
    ("👥", "Clients",    "clients"),
    ("🗂", "Projects",   "projects"),
    ("✅", "Tasks",      "tasks"),
    ("📄", "Invoices",   "invoices"),
    ("📊", "Reports",    "reports"),
]


class AppWindow(tk.Tk):
    """Root application window.

    Owns the sidebar navigation and a single content frame whose
    children are replaced whenever the user navigates to a new screen.

    Args:
        freelancer: The authenticated freelancer profile loaded at startup.
    """

    def __init__(self, freelancer: Freelancer) -> None:
        super().__init__()
        self._freelancer = freelancer
        self._current_screen = None
        self._screen_cache: dict = {}

        self.title("Freelance Project Manager")
        self.configure(bg=BG_DARK)
        self.minsize(1000, 640)

        # Centre window
        self.update_idletasks()
        w, h = 1200, 720
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Configure global ttk style
        self._configure_style()

        self._build_layout()
        self.navigate("dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #

    def _configure_style(self) -> None:
        """Set global ttk widget styles."""
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG_DARK, foreground=FG_PRIMARY)
        style.configure("TPanedwindow", background=BG_DARK)
        style.configure("Sash", sashthickness=4, background=BORDER)

    def _build_layout(self) -> None:
        """Create the sidebar + content split layout."""
        # ── Top bar ───────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=BG_PANEL, height=48, pady=0)
        topbar.pack(fill=tk.X, side=tk.TOP)
        topbar.pack_propagate(False)

        tk.Label(topbar, text="⚡ Freelance Manager",
                 font=FONT_H3, bg=BG_PANEL, fg=FG_PRIMARY,
                 padx=16).pack(side=tk.LEFT, pady=10)

        # Freelancer name badge (top right)
        name = self._freelancer.full_name
        tk.Label(topbar, text=f"👤  {name}", font=FONT_SMALL,
                 bg=BG_PANEL, fg=FG_SECONDARY, padx=16).pack(side=tk.RIGHT, pady=10)

        # Thin accent line under topbar
        tk.Frame(self, bg=ACCENT, height=2).pack(fill=tk.X)

        # ── Main area ─────────────────────────────────────────────────
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self._sidebar = tk.Frame(main, bg=BG_PANEL, width=SIDEBAR_W)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # Thin vertical border
        tk.Frame(main, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Content area
        self._content = tk.Frame(main, bg=BG_DARK)
        self._content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_sidebar(self) -> None:
        """Populate the sidebar with navigation buttons."""
        tk.Frame(self._sidebar, bg=BG_PANEL, height=12).pack()  # top spacer

        self._nav_buttons: dict[str, tk.Button] = {}

        for icon, label, key in NAV_ITEMS:
            btn = tk.Button(
                self._sidebar,
                text=f"  {icon}  {label}",
                font=FONT_BODY,
                bg=BG_PANEL,
                fg=FG_SECONDARY,
                activebackground=BG_CARD,
                activeforeground=FG_PRIMARY,
                relief="flat",
                anchor="w",
                cursor="hand2",
                pady=10,
                padx=8,
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill=tk.X, padx=8, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BG_CARD, fg=FG_PRIMARY)
                     if b.cget("bg") != ACCENT else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_PANEL, fg=FG_SECONDARY)
                     if b.cget("bg") != ACCENT else None)
            self._nav_buttons[key] = btn

        # Spacer then settings/profile at bottom
        tk.Frame(self._sidebar, bg=BG_PANEL).pack(fill=tk.Y, expand=True)
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(fill=tk.X, padx=8)

        settings_btn = tk.Button(
            self._sidebar,
            text="  ⚙  Settings",
            font=FONT_BODY,
            bg=BG_PANEL, fg=FG_MUTED,
            activebackground=BG_CARD, activeforeground=FG_PRIMARY,
            relief="flat", anchor="w", cursor="hand2",
            pady=10, padx=8,
            command=self._open_settings,
        )
        settings_btn.pack(fill=tk.X, padx=8, pady=(4, 12))

    def _set_active_nav(self, key: str) -> None:
        """Highlight the active sidebar button."""
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.config(bg=ACCENT, fg=FG_PRIMARY)
            else:
                btn.config(bg=BG_PANEL, fg=FG_SECONDARY)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #

    def navigate(self, screen_key: str) -> None:
        """Switch to the named screen.

        Screens are lazy-loaded and cached. Each screen is a Frame that
        fills the content area.

        Args:
            screen_key: One of 'dashboard', 'clients', 'projects',
                        'tasks', 'invoices', 'reports'.
        """
        self._set_active_nav(screen_key)

        # Destroy the current screen
        for widget in self._content.winfo_children():
            widget.destroy()

        # Build or rebuild the requested screen
        screen = self._build_screen(screen_key)
        self._current_screen = screen_key

    def _build_screen(self, key: str) -> tk.Frame:
        """Instantiate and return the requested screen frame.

        Args:
            key: Screen identifier string.

        Returns:
            The constructed screen Frame (already packed into content area).
        """
        if key == "dashboard":
            from src.gui.dashboard import DashboardFrame
            return DashboardFrame(self._content, self._freelancer)

        elif key == "clients":
            from src.gui.clients import ClientsFrame
            return ClientsFrame(self._content)

        elif key == "projects":
            from src.gui.projects import ProjectsFrame
            return ProjectsFrame(self._content)

        elif key == "tasks":
            from src.gui.tasks import TasksFrame
            return TasksFrame(self._content)

        elif key == "invoices":
            from src.gui.invoices import InvoicesFrame
            return InvoicesFrame(self._content)

        elif key == "reports":
            from src.gui.reports import ReportsFrame
            return ReportsFrame(self._content)

        else:
            tk.Label(self._content, text=f"Unknown screen: {key}",
                     bg=BG_DARK, fg=FG_PRIMARY).pack(expand=True)
            return self._content

    # ------------------------------------------------------------------ #
    # Settings / Profile editor
    # ------------------------------------------------------------------ #

    def _open_settings(self) -> None:
        """Open the settings / profile editor dialog."""
        SettingsDialog(self, self._freelancer, on_save=self._on_profile_saved)

    def _on_profile_saved(self, freelancer: Freelancer) -> None:
        """Update the in-memory profile and refresh the topbar."""
        self._freelancer = freelancer
        # Refresh topbar name
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget("bg") == BG_PANEL:
                for child in widget.winfo_children():
                    child.destroy()
                tk.Label(widget, text="⚡ Freelance Manager",
                         font=FONT_H3, bg=BG_PANEL, fg=FG_PRIMARY,
                         padx=16).pack(side=tk.LEFT, pady=10)
                tk.Label(widget, text=f"👤  {freelancer.full_name}",
                         font=FONT_SMALL, bg=BG_PANEL, fg=FG_SECONDARY,
                         padx=16).pack(side=tk.RIGHT, pady=10)
                break
        # Re-navigate to dashboard to refresh
        self.navigate("dashboard")

    # ------------------------------------------------------------------ #
    # Close handler
    # ------------------------------------------------------------------ #

    def _on_close(self) -> None:
        """Confirm and close the application."""
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?", parent=self):
            from src.database.db_manager import DatabaseManager
            DatabaseManager().close()
            self.destroy()


# ====================================================================== #
# Settings dialog
# ====================================================================== #

class SettingsDialog(tk.Toplevel):
    """Profile editor accessible from the sidebar settings button."""

    def __init__(self, parent: AppWindow, freelancer: Freelancer, on_save) -> None:
        super().__init__(parent)
        self.title("Settings — Edit Profile")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.grab_set()
        self._freelancer = freelancer
        self._on_save = on_save
        self._repo = FreelancerRepository()

        w, h = 480, 440
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._vars = {
            "full_name": tk.StringVar(value=freelancer.full_name),
            "email": tk.StringVar(value=freelancer.email),
            "phone": tk.StringVar(value=freelancer.phone),
            "profession": tk.StringVar(value=freelancer.profession),
            "hourly_rate": tk.StringVar(value=str(freelancer.hourly_rate)),
            "tax_number": tk.StringVar(value=freelancer.tax_number),
        }
        self._build_ui()

    def _build_ui(self) -> None:
        from src.gui.widgets import field_row, make_button
        body = tk.Frame(self, bg=BG_DARK, padx=32, pady=24)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Edit Profile", font=FONT_H3,
                 bg=BG_DARK, fg=FG_PRIMARY).pack(anchor="w", pady=(0, 16))

        fields = [
            ("Full Name *", "full_name"),
            ("Email *", "email"),
            ("Phone", "phone"),
            ("Profession", "profession"),
            ("Default Hourly Rate ($)", "hourly_rate"),
            ("Tax / VAT Number", "tax_number"),
        ]
        for label, key in fields:
            field_row(body, label, self._vars[key], bg=BG_DARK)

        tk.Frame(body, bg=BG_DARK, height=16).pack()
        make_button(body, "Save Changes", self._save, width=20).pack()

    def _save(self) -> None:
        name = self._vars["full_name"].get().strip()
        email = self._vars["email"].get().strip()
        if not name or not email:
            messagebox.showwarning("Validation", "Name and email are required.", parent=self)
            return
        try:
            rate = float(self._vars["hourly_rate"].get() or 0)
        except ValueError:
            messagebox.showwarning("Validation", "Hourly rate must be a number.", parent=self)
            return
        try:
            self._freelancer.full_name = name
            self._freelancer.email = email
            self._freelancer.phone = self._vars["phone"].get().strip()
            self._freelancer.profession = self._vars["profession"].get().strip()
            self._freelancer.hourly_rate = rate
            self._freelancer.tax_number = self._vars["tax_number"].get().strip()
            self._repo.save(self._freelancer)
            self._on_save(self._freelancer)
            self.destroy()
        except ValueError as exc:
            messagebox.showerror("Invalid Data", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)
