"""InvoiceRepository — CRUD for Invoice entities."""

from typing import List, Optional
from src.models.invoice import Invoice
from ._base import get_db


class InvoiceRepository:
    """Handles persistence of Invoice objects."""

    def save(self, invoice: Invoice) -> Invoice:
        """Insert or update an Invoice record."""
        db = get_db()
        try:
            if invoice.invoice_id == 0:
                cursor = db.execute(
                    """
                    INSERT INTO invoices
                        (invoice_number, client_id, project_id, amount, issue_date, due_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (invoice.invoice_number, invoice.client_id, invoice.project_id,
                     invoice.amount, invoice.issue_date, invoice.due_date, invoice.status),
                )
                invoice.invoice_id = cursor.lastrowid
            else:
                db.execute(
                    """
                    UPDATE invoices
                    SET invoice_number=?, client_id=?, project_id=?, amount=?,
                        issue_date=?, due_date=?, status=?
                    WHERE id=?
                    """,
                    (invoice.invoice_number, invoice.client_id, invoice.project_id,
                     invoice.amount, invoice.issue_date, invoice.due_date,
                     invoice.status, invoice.invoice_id),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"InvoiceRepository.save failed: {exc}") from exc
        return invoice

    def find_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Retrieve an Invoice by its primary key."""
        db = get_db()
        cursor = db.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        row = cursor.fetchone()
        return self._row_to_invoice(row) if row else None

    def find_all(self) -> List[Invoice]:
        """Retrieve all invoices ordered by issue date descending."""
        db = get_db()
        cursor = db.execute("SELECT * FROM invoices ORDER BY issue_date DESC")
        return [self._row_to_invoice(row) for row in cursor.fetchall()]

    def find_by_project(self, project_id: int) -> List[Invoice]:
        """Retrieve all invoices for a given project."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM invoices WHERE project_id=? ORDER BY issue_date DESC",
            (project_id,),
        )
        return [self._row_to_invoice(row) for row in cursor.fetchall()]

    def find_pending(self) -> List[Invoice]:
        """Retrieve all invoices with status 'pending' or 'sent'."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM invoices WHERE status IN ('pending', 'sent') ORDER BY due_date"
        )
        return [self._row_to_invoice(row) for row in cursor.fetchall()]

    def total_income(self) -> float:
        """Sum all paid invoice amounts."""
        db = get_db()
        cursor = db.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM invoices WHERE status='paid'"
        )
        row = cursor.fetchone()
        return float(row["total"]) if row else 0.0

    def number_exists(self, invoice_number: str) -> bool:
        """Check whether an invoice number already exists."""
        db = get_db()
        cursor = db.execute(
            "SELECT 1 FROM invoices WHERE invoice_number=?", (invoice_number,)
        )
        return cursor.fetchone() is not None

    def delete(self, invoice_id: int) -> bool:
        """Delete an invoice by primary key."""
        db = get_db()
        cursor = db.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _row_to_invoice(row) -> Invoice:
        return Invoice(
            invoice_number=row["invoice_number"],
            client_id=row["client_id"] or 0,
            project_id=row["project_id"] or 0,
            amount=row["amount"],
            issue_date=row["issue_date"],
            due_date=row["due_date"],
            status=row["status"],
            invoice_id=row["id"],
        )
