"""InvoiceService — business logic for invoice management."""

from datetime import date, timedelta
from typing import List

from src.models.invoice import Invoice
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.project_repository import ProjectRepository
from src.strategies.billing_strategy import get_strategy
from src.exceptions.app_exceptions import (
    InvoiceAlreadyPaidException,
    DuplicateInvoiceException,
)


class InvoiceService:
    """Provides business logic for creating, paying, and listing invoices."""

    def __init__(self) -> None:
        self._repo = InvoiceRepository()
        self._project_repo = ProjectRepository()

    def generate_invoice(
        self,
        project_id: int,
        client_id: int,
        invoice_number: str = "",
        amount: float = 0.0,
        due_days: int = 30,
    ) -> Invoice:
        """Generate and save an invoice for a project.

        If amount is 0, the project's billing strategy is used to calculate it.

        Args:
            project_id: The project to invoice.
            client_id: The client to bill.
            invoice_number: Custom number (auto-generated if empty).
            amount: Invoice total (0 = auto-calculate from strategy).
            due_days: Days from today until payment is due.

        Returns:
            The saved Invoice.

        Raises:
            DuplicateInvoiceException: If invoice_number already exists.
        """
        try:
            today = str(date.today())
            due = str(date.today() + timedelta(days=due_days))

            # Auto-generate invoice number if not provided
            if not invoice_number:
                count = len(self._repo.find_all()) + 1
                invoice_number = f"INV-{date.today().year}-{count:04d}"

            if self._repo.number_exists(invoice_number):
                raise DuplicateInvoiceException(invoice_number)

            # Auto-calculate if amount not specified
            if amount == 0.0:
                _, _, amount = self.preview_amount(project_id)

            invoice = Invoice(
                invoice_number=invoice_number,
                client_id=client_id,
                project_id=project_id,
                amount=amount,
                issue_date=today,
                due_date=due,
            )
            return self._repo.save(invoice)
        except DuplicateInvoiceException:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to generate invoice: {exc}") from exc
        finally:
            pass  # logging hook

    def preview_amount(self, project_id: int) -> tuple[float, float, float]:
        """Preview invoice amount breakdown (strategy, expenses, total).

        Returns:
            Tuple: (strategy_amount, billable_expenses, total_amount)
        """
        project = self._project_repo.find_by_id(project_id)
        if not project:
            return 0.0, 0.0, 0.0

        try:
            from src.repositories.milestone_repository import MilestoneRepository
            from src.repositories.task_repository import TaskRepository
            from src.repositories.expense_repository import ExpenseRepository
            
            ms_repo = MilestoneRepository()
            task_repo = TaskRepository()
            exp_repo = ExpenseRepository()
            
            milestones = ms_repo.find_by_project(project_id)
            for m in milestones:
                tasks = task_repo.find_by_milestone(m.milestone_id)
                for t in tasks:
                    m.add_task(t)
                project.add_milestone(m)
            
            strategy = get_strategy(project.billing_type)
            project.billing_strategy = strategy
            strategy_amount = project.calculate_invoice_amount()
            
            expenses = exp_repo.find_by_project(project_id)
            billable_expenses = sum(e.amount for e in expenses if e.is_billable())
            
            return strategy_amount, billable_expenses, strategy_amount + billable_expenses
        except Exception as exc:
            raise RuntimeError(f"Failed to preview invoice amount: {exc}") from exc


    def mark_paid(self, invoice_id: int) -> Invoice:
        """Mark an invoice as paid.

        Args:
            invoice_id: The invoice's database id.

        Returns:
            The updated Invoice.

        Raises:
            InvoiceAlreadyPaidException: If already paid.
            RuntimeError: If the invoice is not found.
        """
        invoice = self._repo.find_by_id(invoice_id)
        if invoice is None:
            raise RuntimeError(f"Invoice id={invoice_id} not found.")
        try:
            invoice.mark_as_paid()
            self._repo.save(invoice)
        except InvoiceAlreadyPaidException:
            raise
        else:
            return invoice
        finally:
            pass  # logging hook

    def get_all(self) -> List[Invoice]:
        """Return all invoices."""
        return self._repo.find_all()

    def get_pending(self) -> List[Invoice]:
        """Return all pending/unpaid invoices."""
        return self._repo.find_pending()

    def get_total_income(self) -> float:
        """Return total income from all paid invoices."""
        return self._repo.total_income()

    def delete(self, invoice_id: int) -> None:
        """Delete an invoice."""
        self._repo.delete(invoice_id)
