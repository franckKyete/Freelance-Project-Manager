"""ProjectService — business logic for project management."""

from datetime import date
from typing import List, Optional

from src.models.project import Project
from src.models.milestone import Milestone
from src.models.expense import Expense
from src.repositories.project_repository import ProjectRepository
from src.repositories.milestone_repository import MilestoneRepository
from src.repositories.expense_repository import ExpenseRepository
from src.repositories.task_repository import TaskRepository
from src.strategies.billing_strategy import get_strategy
from src.exceptions.app_exceptions import (
    BudgetExceededException,
    DeadlinePassedException,
    ClientNotFoundException,
)
from src.utils.validators import validate_date_string


class ProjectService:
    """Business logic for creating and managing projects, milestones, and expenses."""

    def __init__(self) -> None:
        self._project_repo = ProjectRepository()
        self._milestone_repo = MilestoneRepository()
        self._expense_repo = ExpenseRepository()
        self._task_repo = TaskRepository()

    # ------------------------------------------------------------------ #
    # Projects
    # ------------------------------------------------------------------ #

    def create_project(
        self,
        title: str,
        client_id: int,
        budget: float = 0.0,
        description: str = "",
        start_date: str = "",
        deadline: str = "",
        billing_type: str = "hourly",
        billing_rate: float = 0.0,
    ) -> Project:
        """Create and save a new project.

        Args:
            title: Project title.
            client_id: Owning client's id.
            budget: Agreed budget.
            description: Project description.
            start_date: ISO 8601 start date.
            deadline: ISO 8601 deadline.
            billing_type: 'hourly', 'fixed', or 'retainer'.
            billing_rate: Rate for billing calculations.

        Returns:
            The saved Project.

        Raises:
            DeadlinePassedException: If deadline is in the past.
            ValueError: If title is empty or budget negative.
        """
        try:
            if deadline and validate_date_string(deadline):
                if deadline < str(date.today()):
                    raise DeadlinePassedException(
                        f"Deadline {deadline} has already passed."
                    )
            project = Project(
                title=title,
                client_id=client_id,
                description=description,
                budget=budget,
                start_date=start_date or str(date.today()),
                deadline=deadline,
                billing_type=billing_type,
                billing_rate=billing_rate,
            )
            project.billing_strategy = get_strategy(billing_type)
            return self._project_repo.save(project)
        except (ValueError, DeadlinePassedException):
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to create project: {exc}") from exc
        finally:
            pass  # audit/logging hook

    def update_project(self, project: Project) -> Project:
        """Update an existing project record."""
        project.billing_strategy = get_strategy(project.billing_type)
        return self._project_repo.save(project)

    def delete_project(self, project_id: int) -> None:
        """Delete a project and all its children (cascaded by DB)."""
        try:
            self._project_repo.delete(project_id)
        except Exception as exc:
            raise RuntimeError(f"Failed to delete project {project_id}: {exc}") from exc
        else:
            pass
        finally:
            pass

    def get_all_projects(self) -> List[Project]:
        """Return all projects."""
        return self._project_repo.find_all()

    def get_project(self, project_id: int) -> Optional[Project]:
        """Return a single project by id."""
        return self._project_repo.find_by_id(project_id)

    def get_active_projects(self) -> List[Project]:
        """Return all active projects."""
        return self._project_repo.find_active()

    def get_projects_for_client(self, client_id: int) -> List[Project]:
        """Return all projects for a given client."""
        return self._project_repo.find_by_client(client_id)

    # ------------------------------------------------------------------ #
    # Milestones
    # ------------------------------------------------------------------ #

    def add_milestone(self, project_id: int, title: str, due_date: str = "") -> Milestone:
        """Create and attach a milestone to a project."""
        try:
            milestone = Milestone(title=title, due_date=due_date, project_id=project_id)
            return self._milestone_repo.save(milestone)
        except Exception as exc:
            raise RuntimeError(f"Failed to add milestone: {exc}") from exc

    def update_milestone(self, milestone: Milestone) -> Milestone:
        """Update a milestone record."""
        return self._milestone_repo.save(milestone)

    def delete_milestone(self, milestone_id: int) -> None:
        """Delete a milestone."""
        self._milestone_repo.delete(milestone_id)

    def get_milestones(self, project_id: int) -> List[Milestone]:
        """Return all milestones for a project, with tasks loaded."""
        milestones = self._milestone_repo.find_by_project(project_id)
        for m in milestones:
            tasks = self._task_repo.find_by_milestone(m.milestone_id)
            for t in tasks:
                m.add_task(t)
        return milestones

    # ------------------------------------------------------------------ #
    # Expenses
    # ------------------------------------------------------------------ #

    def add_expense(
        self,
        project_id: int,
        amount: float,
        category: str = "General",
        description: str = "",
        date_str: str = "",
        billable: bool = False,
    ) -> Expense:
        """Add an expense to a project.

        Raises:
            BudgetExceededException: If the new expense would exceed budget.
        """
        try:
            project = self._project_repo.find_by_id(project_id)
            if project:
                current_spend = self._expense_repo.total_for_project(project_id)
                if project.budget > 0 and (current_spend + amount) > project.budget:
                    raise BudgetExceededException(
                        f"Adding ${amount:.2f} would exceed the project budget of ${project.budget:.2f}."
                    )
            expense = Expense(
                project_id=project_id,
                amount=amount,
                category=category,
                description=description,
                date=date_str or str(date.today()),
                billable=billable,
            )
            return self._expense_repo.save(expense)
        except BudgetExceededException:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to add expense: {exc}") from exc

    def get_expenses(self, project_id: int) -> List[Expense]:
        """Return all expenses for a project."""
        return self._expense_repo.find_by_project(project_id)

    def delete_expense(self, expense_id: int) -> None:
        """Delete an expense."""
        self._expense_repo.delete(expense_id)
