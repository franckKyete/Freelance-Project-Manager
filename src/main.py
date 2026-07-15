"""Application entry point for the Freelance Project Manager.

Run with:
    python src/main.py

Or from the project root:
    python -m src.main
"""

import sys
import os
import tkinter as tk

# ── Make sure the project root is on sys.path ───────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.database.db_manager import DatabaseManager
from src.repositories.freelancer_repository import FreelancerRepository
from src.exceptions.app_exceptions import ProfileNotFoundException
from src.gui.auth import AuthScreen
from src.gui.app import AppWindow


def main() -> None:
    """Bootstrap the application.

    Steps:
    1. Open the SQLite connection (creates the file + schema if needed).
    2. Check whether a freelancer profile already exists.
       - If not → show the first-run AuthScreen setup wizard.
       - If yes → load the profile directly.
    3. Launch the main AppWindow.
    """
    # ── Step 1: Initialise database ────────────────────────────────────
    db = DatabaseManager()  # Singleton
    try:
        db_path = os.path.join(ROOT, "freelance_manager.db")
        db.connect(db_path)
    except RuntimeError as exc:
        import tkinter.messagebox as mb
        root = tk.Tk()
        root.withdraw()
        mb.showerror("Database Error", str(exc))
        root.destroy()
        sys.exit(1)

    # ── Step 2: Load or create the freelancer profile ──────────────────
    repo = FreelancerRepository()
    freelancer = None

    if not repo.exists():
        # First run: show setup wizard
        root = tk.Tk()
        root.withdraw()  # Hide the blank root window

        auth = AuthScreen(root)
        root.wait_window(auth)

        if auth.profile is None:
            # User closed the dialog without saving → exit cleanly
            db.close()
            root.destroy()
            sys.exit(0)

        freelancer = auth.profile
        root.destroy()
    else:
        try:
            freelancer = repo.load()
        except ProfileNotFoundException:
            # Should not happen (exists() returned True), but guard anyway
            import tkinter.messagebox as mb
            root = tk.Tk()
            root.withdraw()
            mb.showerror("Profile Error",
                         "Could not load freelancer profile. The database may be corrupted.")
            root.destroy()
            db.close()
            sys.exit(1)

    # ── Step 3: Launch main application window ─────────────────────────
    app = AppWindow(freelancer)
    app.mainloop()


if __name__ == "__main__":
    main()
