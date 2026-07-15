"""ReportService — generates financial and productivity summaries."""

from datetime import date
from typing import List, Dict

from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.expense_repository import ExpenseRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.time_entry_repository import TimeEntryRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.milestone_repository import MilestoneRepository
from src.utils.validators import format_currency, format_hours


class ReportService:
    """Generates various financial and productivity reports.

    All reports are returned as plain dictionaries containing structured
    data that the GUI can display as tables or summaries.
    """

    def __init__(self) -> None:
        self._invoice_repo = InvoiceRepository()
        self._expense_repo = ExpenseRepository()
        self._project_repo = ProjectRepository()
        self._time_repo = TimeEntryRepository()
        self._task_repo = TaskRepository()
        self._milestone_repo = MilestoneRepository()

    def income_report(self) -> Dict:
        """Generate a summary of all invoice income.

        Returns:
            Dictionary with 'total_income', 'paid_count', 'pending_count',
            'pending_amount', and 'rows' (list of invoice dicts).
        """
        try:
            all_invoices = self._invoice_repo.find_all()
            paid = [i for i in all_invoices if i.status == "paid"]
            pending = [i for i in all_invoices if i.status in ("pending", "sent")]
            rows = []
            for inv in all_invoices:
                rows.append({
                    "Invoice #": inv.invoice_number,
                    "Issue Date": inv.issue_date,
                    "Due Date": inv.due_date,
                    "Amount": format_currency(inv.amount),
                    "Status": inv.status.upper(),
                })
            return {
                "title": "Income Report",
                "total_income": format_currency(sum(i.amount for i in paid)),
                "paid_count": len(paid),
                "pending_count": len(pending),
                "pending_amount": format_currency(sum(i.amount for i in pending)),
                "rows": rows,
                "columns": ["Invoice #", "Issue Date", "Due Date", "Amount", "Status"],
            }
        except Exception as exc:
            raise RuntimeError(f"Income report failed: {exc}") from exc

    def expense_report(self) -> Dict:
        """Generate a summary of all project expenses.

        Returns:
            Dictionary with 'total_expenses', 'by_category', and 'rows'.
        """
        try:
            projects = self._project_repo.find_all()
            rows = []
            category_totals: Dict[str, float] = {}
            for project in projects:
                expenses = self._expense_repo.find_by_project(project.project_id)
                for exp in expenses:
                    rows.append({
                        "Project": project.title,
                        "Category": exp.category,
                        "Description": exp.description,
                        "Amount": format_currency(exp.amount),
                        "Date": exp.date,
                        "Billable": "Yes" if exp.is_billable() else "No",
                    })
                    category_totals[exp.category] = (
                        category_totals.get(exp.category, 0) + exp.amount
                    )
            total = sum(category_totals.values())
            return {
                "title": "Expense Report",
                "total_expenses": format_currency(total),
                "by_category": {k: format_currency(v) for k, v in category_totals.items()},
                "rows": rows,
                "columns": ["Project", "Category", "Description", "Amount", "Date", "Billable"],
            }
        except Exception as exc:
            raise RuntimeError(f"Expense report failed: {exc}") from exc

    def productivity_report(self) -> Dict:
        """Generate a productivity breakdown across all projects.

        Returns:
            Dictionary with hours per project and overall totals.
        """
        try:
            projects = self._project_repo.find_all()
            rows = []
            total_hours = 0.0
            for project in projects:
                milestones = self._milestone_repo.find_by_project(project.project_id)
                proj_hours = 0.0
                for m in milestones:
                    tasks = self._task_repo.find_by_milestone(m.milestone_id)
                    for t in tasks:
                        proj_hours += t.completed_hours
                total_hours += proj_hours
                rows.append({
                    "Project": project.title,
                    "Status": project.status.title(),
                    "Hours Logged": format_hours(proj_hours),
                    "Progress": f"{project.calculate_progress() * 100:.0f}%",
                })
            return {
                "title": "Productivity Report",
                "total_hours": format_hours(total_hours),
                "weekly_hours": format_hours(self._time_repo.total_hours_this_week()),
                "rows": rows,
                "columns": ["Project", "Status", "Hours Logged", "Progress"],
            }
        except Exception as exc:
            raise RuntimeError(f"Productivity report failed: {exc}") from exc

    def profit_report(self) -> Dict:
        """Generate a profit analysis per project.

        Returns:
            Dictionary with profit per project and overall net profit.
        """
        try:
            projects = self._project_repo.find_all()
            rows = []
            net_profit = 0.0
            for project in projects:
                income = sum(
                    i.amount for i in self._invoice_repo.find_by_project(project.project_id)
                    if i.status == "paid"
                )
                expenses = self._expense_repo.total_for_project(project.project_id)
                profit = income - expenses
                net_profit += profit
                rows.append({
                    "Project": project.title,
                    "Income": format_currency(income),
                    "Expenses": format_currency(expenses),
                    "Profit": format_currency(profit),
                    "Margin": f"{(profit / income * 100):.1f}%" if income > 0 else "N/A",
                })
            return {
                "title": "Profit Report",
                "net_profit": format_currency(net_profit),
                "rows": rows,
                "columns": ["Project", "Income", "Expenses", "Profit", "Margin"],
            }
        except Exception as exc:
            raise RuntimeError(f"Profit report failed: {exc}") from exc
