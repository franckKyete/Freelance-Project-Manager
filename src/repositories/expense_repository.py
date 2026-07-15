"""ExpenseRepository — CRUD for Expense entities."""

from typing import List, Optional
from src.models.expense import Expense
from ._base import get_db


class ExpenseRepository:
    """Handles persistence of Expense objects."""

    def save(self, expense: Expense) -> Expense:
        """Insert or update an Expense record."""
        db = get_db()
        try:
            if expense.expense_id == 0:
                cursor = db.execute(
                    "INSERT INTO expenses (project_id, category, description, amount, date, billable) VALUES (?, ?, ?, ?, ?, ?)",
                    (expense.project_id, expense.category, expense.description,
                     expense.amount, expense.date, int(expense.is_billable())),
                )
                expense.expense_id = cursor.lastrowid
            else:
                db.execute(
                    "UPDATE expenses SET project_id=?, category=?, description=?, amount=?, date=?, billable=? WHERE id=?",
                    (expense.project_id, expense.category, expense.description,
                     expense.amount, expense.date, int(expense.is_billable()), expense.expense_id),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"ExpenseRepository.save failed: {exc}") from exc
        return expense

    def find_by_project(self, project_id: int) -> List[Expense]:
        """Retrieve all expenses for a project."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM expenses WHERE project_id=? ORDER BY date DESC",
            (project_id,),
        )
        return [self._row_to_expense(row) for row in cursor.fetchall()]

    def total_for_project(self, project_id: int) -> float:
        """Sum all expense amounts for a project."""
        db = get_db()
        cursor = db.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE project_id=?",
            (project_id,),
        )
        row = cursor.fetchone()
        return float(row["total"]) if row else 0.0

    def delete(self, expense_id: int) -> bool:
        """Delete an expense by primary key."""
        db = get_db()
        cursor = db.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _row_to_expense(row) -> Expense:
        return Expense(
            project_id=row["project_id"] or 0,
            amount=row["amount"],
            category=row["category"],
            description=row["description"],
            date=row["date"],
            billable=bool(row["billable"]),
            expense_id=row["id"],
        )
