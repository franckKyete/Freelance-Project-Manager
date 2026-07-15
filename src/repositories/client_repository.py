"""ClientRepository — CRUD operations for Client entities."""

from typing import List, Optional
from src.models.client import Client
from ._base import get_db


class ClientRepository:
    """Handles persistence of Client objects using SQLite.

    All SQL is isolated here; no SQL appears in service or GUI layers.
    """

    def save(self, client: Client) -> Client:
        """Insert or update a Client record.

        If client.id == 0, an INSERT is performed and the new id is
        assigned back to the object. Otherwise an UPDATE is performed.

        Args:
            client: The Client instance to persist.

        Returns:
            The same Client with its id populated after INSERT.
        """
        db = get_db()
        try:
            if client.id == 0:
                cursor = db.execute(
                    """
                    INSERT INTO clients
                        (full_name, email, phone, company_name, address, preferred_payment_method)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client.full_name, client.email, client.phone,
                        client.company_name, client.address,
                        client.preferred_payment_method,
                    ),
                )
                client.id = cursor.lastrowid
            else:
                db.execute(
                    """
                    UPDATE clients
                    SET full_name=?, email=?, phone=?, company_name=?,
                        address=?, preferred_payment_method=?
                    WHERE id=?
                    """,
                    (
                        client.full_name, client.email, client.phone,
                        client.company_name, client.address,
                        client.preferred_payment_method, client.id,
                    ),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"ClientRepository.save failed: {exc}") from exc
        return client

    def find_by_id(self, client_id: int) -> Optional[Client]:
        """Retrieve a Client by its primary key.

        Args:
            client_id: The database id to look up.

        Returns:
            A Client instance, or None if not found.
        """
        db = get_db()
        cursor = db.execute("SELECT * FROM clients WHERE id=?", (client_id,))
        row = cursor.fetchone()
        return self._row_to_client(row) if row else None

    def find_all(self) -> List[Client]:
        """Retrieve all clients ordered by name.

        Returns:
            List of Client instances (may be empty).
        """
        db = get_db()
        cursor = db.execute("SELECT * FROM clients ORDER BY full_name")
        return [self._row_to_client(row) for row in cursor.fetchall()]

    def delete(self, client_id: int) -> bool:
        """Delete a client by primary key.

        Args:
            client_id: The database id of the client to delete.

        Returns:
            True if a record was deleted, False otherwise.
        """
        db = get_db()
        cursor = db.execute("DELETE FROM clients WHERE id=?", (client_id,))
        db.commit()
        return cursor.rowcount > 0

    def search(self, query: str) -> List[Client]:
        """Search clients by name or company name (case-insensitive).

        Args:
            query: Partial name or company string to match.

        Returns:
            List of matching Client instances.
        """
        db = get_db()
        pattern = f"%{query}%"
        cursor = db.execute(
            "SELECT * FROM clients WHERE full_name LIKE ? OR company_name LIKE ?",
            (pattern, pattern),
        )
        return [self._row_to_client(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_client(row) -> Client:
        """Convert a sqlite3.Row to a Client instance.

        Args:
            row: A sqlite3.Row from the clients table.

        Returns:
            Populated Client instance.
        """
        return Client(
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            company_name=row["company_name"],
            address=row["address"],
            preferred_payment_method=row["preferred_payment_method"],
            client_id=row["id"],
        )
