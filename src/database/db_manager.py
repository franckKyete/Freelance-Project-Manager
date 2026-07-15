"""Singleton DatabaseManager for the Freelance Project Manager.

Design Pattern: **Singleton**
Only one SQLite connection is created for the entire application lifetime.
All repositories obtain the same DatabaseManager instance via DatabaseManager().

Example:
    db = DatabaseManager()
    db.connect("mydata.db")
    cursor = db.execute("SELECT * FROM clients")
    rows = cursor.fetchall()
    db.commit()
    db.close()
"""

import sqlite3
import os
from typing import Optional


class DatabaseManager:
    """Singleton that manages the single SQLite database connection.

    Attributes:
        _instance: Class-level reference to the sole instance.
        _connection: The active sqlite3 connection object.
    """

    _instance: Optional["DatabaseManager"] = None
    _connection: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------ #
    # Singleton boilerplate
    # ------------------------------------------------------------------ #

    def __new__(cls) -> "DatabaseManager":
        """Return the existing instance or create one on first call.

        Returns:
            The single DatabaseManager instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------ #
    # Public interface
    # ------------------------------------------------------------------ #

    def connect(self, db_path: str = "freelance_manager.db") -> None:
        """Open the SQLite connection and initialise the schema.

        If a connection is already open this method is a no-op.

        Args:
            db_path: Path to the SQLite database file.
                     Created automatically if it does not exist.
        """
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(db_path)
                self._connection.row_factory = sqlite3.Row
                self._connection.execute("PRAGMA foreign_keys = ON")
                self._initialize_schema()
            except sqlite3.Error as exc:
                raise RuntimeError(f"Failed to open database '{db_path}': {exc}") from exc

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a parameterised SQL statement.

        Args:
            sql: The SQL string (use ? placeholders).
            params: Tuple of values bound to the placeholders.

        Returns:
            The resulting sqlite3.Cursor.

        Raises:
            RuntimeError: If no connection has been opened.
            sqlite3.Error: On any SQL error.
        """
        if self._connection is None:
            raise RuntimeError("No database connection. Call connect() first.")
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor

    def commit(self) -> None:
        """Commit the current transaction."""
        if self._connection:
            self._connection.commit()

    def close(self) -> None:
        """Close the database connection and reset the cached reference."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # ------------------------------------------------------------------ #
    # Schema
    # ------------------------------------------------------------------ #

    def _initialize_schema(self) -> None:
        """Create all application tables if they do not already exist."""
        statements = [
            # Freelancer profile (single row)
            """
            CREATE TABLE IF NOT EXISTS freelancer_profile (
                id                  INTEGER PRIMARY KEY,
                full_name           TEXT    NOT NULL,
                email               TEXT    NOT NULL,
                phone               TEXT    DEFAULT '',
                profession          TEXT    DEFAULT '',
                hourly_rate         REAL    DEFAULT 0,
                tax_number          TEXT    DEFAULT '',
                years_of_experience INTEGER DEFAULT 0,
                is_senior           INTEGER DEFAULT 0
            )
            """,
            # Clients
            """
            CREATE TABLE IF NOT EXISTS clients (
                id                       INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name                TEXT    NOT NULL,
                email                    TEXT    NOT NULL,
                phone                    TEXT    DEFAULT '',
                company_name             TEXT    DEFAULT '',
                address                  TEXT    DEFAULT '',
                preferred_payment_method TEXT    DEFAULT 'Bank Transfer'
            )
            """,
            # Projects
            """
            CREATE TABLE IF NOT EXISTS projects (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT    NOT NULL,
                description  TEXT    DEFAULT '',
                budget       REAL    DEFAULT 0,
                start_date   TEXT    DEFAULT '',
                deadline     TEXT    DEFAULT '',
                status       TEXT    DEFAULT 'active',
                billing_type TEXT    DEFAULT 'hourly',
                billing_rate REAL    DEFAULT 0,
                client_id    INTEGER,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
            )
            """,
            # Milestones
            """
            CREATE TABLE IF NOT EXISTS milestones (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                due_date   TEXT    DEFAULT '',
                status     TEXT    DEFAULT 'pending',
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """,
            # Tasks
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                title                TEXT    NOT NULL,
                description          TEXT    DEFAULT '',
                estimated_hours      REAL    DEFAULT 0,
                completed_hours      REAL    DEFAULT 0,
                priority             TEXT    DEFAULT 'medium',
                status               TEXT    DEFAULT 'todo',
                task_type            TEXT    NOT NULL DEFAULT 'development',
                programming_language TEXT    DEFAULT '',
                api_type             TEXT    DEFAULT '',
                software_used        TEXT    DEFAULT '',
                word_target          INTEGER DEFAULT 0,
                milestone_id         INTEGER,
                FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE
            )
            """,
            # Time entries
            """
            CREATE TABLE IF NOT EXISTS time_entries (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id    INTEGER,
                start_time TEXT    DEFAULT '',
                end_time   TEXT    DEFAULT '',
                duration   REAL    DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
            """,
            # Expenses
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER,
                category    TEXT    DEFAULT 'General',
                description TEXT    DEFAULT '',
                amount      REAL    DEFAULT 0,
                date        TEXT    DEFAULT '',
                billable    INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """,
            # Invoices
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT    UNIQUE NOT NULL,
                client_id      INTEGER,
                project_id     INTEGER,
                amount         REAL    DEFAULT 0,
                issue_date     TEXT    DEFAULT '',
                due_date       TEXT    DEFAULT '',
                status         TEXT    DEFAULT 'pending',
                FOREIGN KEY (client_id)  REFERENCES clients(id)  ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
            """,
        ]

        try:
            for stmt in statements:
                self._connection.execute(stmt)
            self._connection.commit()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Schema initialisation failed: {exc}") from exc
