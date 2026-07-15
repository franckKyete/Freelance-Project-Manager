"""Utility helpers shared by all repositories."""

from src.database.db_manager import DatabaseManager


def get_db() -> DatabaseManager:
    """Return the singleton DatabaseManager instance.

    Returns:
        The application-wide DatabaseManager.
    """
    return DatabaseManager()
