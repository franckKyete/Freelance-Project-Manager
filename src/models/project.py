"""Project model — Composite pattern root node."""

from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .milestone import Milestone
    from .expense import Expense
    from .invoice import Invoice

STATUS_OPTIONS = ("active", "on_hold", "completed", "cancelled")
BILLING_TYPES = ("hourly", "fixed", "retainer")


class Project:
    """Represents a client project managed by the freelancer.

    Design Pattern: **Composite** — root node.
    Design Pattern: **Strategy** — delegates billing to a BillingStrategy.

    Attributes (private):
        __project_id: Database primary key.
        __client_id: FK of the owning client.
        __title: Project title.
        __description: Detailed description.
        __budget: Agreed budget amount (> 0).
        __start_date: ISO 8601 start date.
        __deadline: ISO 8601 deadline.
        __status: One of STATUS_OPTIONS.
        __billing_type: One of BILLING_TYPES.
        __billing_rate: Rate used by the billing strategy.
        __milestones: List of Milestone objects.
        __expenses: List of Expense objects.
        __invoices: List of Invoice objects.
        __billing_strategy: Optional BillingStrategy instance.
    """

    def __init__(
        self,
        title: str,
        client_id: int = 0,
        description: str = "",
        budget: float = 0.0,
        start_date: str = "",
        deadline: str = "",
        status: str = "active",
        billing_type: str = "hourly",
        billing_rate: float = 0.0,
        project_id: int = 0,
    ) -> None:
        """Initialise a Project.

        Args:
            title: Project title (non-empty).
            client_id: FK of the owning client.
            description: Detailed project description.
            budget: Agreed budget amount (must be >= 0).
            start_date: ISO 8601 start date string.
            deadline: ISO 8601 deadline string.
            status: One of STATUS_OPTIONS.
            billing_type: One of BILLING_TYPES.
            billing_rate: Hourly rate / fixed price / monthly retainer.
            project_id: Database primary key.

        Raises:
            ValueError: If title is empty, budget negative, or enums invalid.
        """
        self.__project_id: int = project_id
        self.__client_id: int = client_id
        self.title = title          # setter validates
        self.__description: str = description
        self.budget = budget        # setter validates
        self.__start_date: str = start_date
        self.__deadline: str = deadline
        self.status = status        # setter validates
        self.billing_type = billing_type  # setter validates
        self.__billing_rate: float = float(billing_rate)
        self.__milestones: List["Milestone"] = []
        self.__expenses: List["Expense"] = []
        self.__invoices: List["Invoice"] = []
        self.__billing_strategy = None

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def project_id(self) -> int:
        """int: Database primary key."""
        return self.__project_id

    @project_id.setter
    def project_id(self, value: int) -> None:
        self.__project_id = int(value)

    @property
    def client_id(self) -> int:
        """int: FK of the owning client."""
        return self.__client_id

    @client_id.setter
    def client_id(self, value: int) -> None:
        self.__client_id = int(value)

    @property
    def title(self) -> str:
        """str: Project title."""
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("Project title cannot be empty.")
        self.__title = value

    @property
    def description(self) -> str:
        """str: Project description."""
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value

    @property
    def budget(self) -> float:
        """float: Agreed project budget (must be >= 0)."""
        return self.__budget

    @budget.setter
    def budget(self, value: float) -> None:
        if value < 0:
            raise ValueError("budget cannot be negative.")
        self.__budget = float(value)

    @property
    def start_date(self) -> str:
        """str: ISO 8601 project start date."""
        return self.__start_date

    @start_date.setter
    def start_date(self, value: str) -> None:
        self.__start_date = value.strip()

    @property
    def deadline(self) -> str:
        """str: ISO 8601 project deadline."""
        return self.__deadline

    @deadline.setter
    def deadline(self, value: str) -> None:
        self.__deadline = value.strip()

    @property
    def status(self) -> str:
        """str: Current project status."""
        return self.__status

    @status.setter
    def status(self, value: str) -> None:
        value = value.lower().strip()
        if value not in STATUS_OPTIONS:
            raise ValueError(f"status must be one of {STATUS_OPTIONS}.")
        self.__status = value

    @property
    def billing_type(self) -> str:
        """str: Billing model type."""
        return self.__billing_type

    @billing_type.setter
    def billing_type(self, value: str) -> None:
        value = value.lower().strip()
        if value not in BILLING_TYPES:
            raise ValueError(f"billing_type must be one of {BILLING_TYPES}.")
        self.__billing_type = value

    @property
    def billing_rate(self) -> float:
        """float: Rate used by the billing strategy."""
        return self.__billing_rate

    @billing_rate.setter
    def billing_rate(self, value: float) -> None:
        if value < 0:
            raise ValueError("billing_rate cannot be negative.")
        self.__billing_rate = float(value)

    @property
    def milestones(self) -> List["Milestone"]:
        """List[Milestone]: Read-only view of project milestones."""
        return list(self.__milestones)

    @property
    def expenses(self) -> List["Expense"]:
        """List[Expense]: Read-only view of project expenses."""
        return list(self.__expenses)

    @property
    def invoices(self) -> List["Invoice"]:
        """List[Invoice]: Read-only view of project invoices."""
        return list(self.__invoices)

    @property
    def billing_strategy(self):
        """BillingStrategy: The active billing strategy."""
        return self.__billing_strategy

    @billing_strategy.setter
    def billing_strategy(self, strategy) -> None:
        self.__billing_strategy = strategy

    # ------------------------------------------------------------------ #
    # Composite methods
    # ------------------------------------------------------------------ #

    def add_milestone(self, milestone: "Milestone") -> None:
        """Add a milestone to the project.

        Args:
            milestone: The Milestone to add.
        """
        self.__milestones.append(milestone)

    def remove_milestone(self, milestone_id: int) -> bool:
        """Remove a milestone by its id.

        Args:
            milestone_id: Database id of the milestone to remove.

        Returns:
            True if removed, False if not found.
        """
        original = len(self.__milestones)
        self.__milestones = [m for m in self.__milestones if m.milestone_id != milestone_id]
        return len(self.__milestones) < original

    def add_expense(self, expense: "Expense") -> None:
        """Add an expense record to the project."""
        self.__expenses.append(expense)

    def add_invoice(self, invoice: "Invoice") -> None:
        """Add an invoice record to the project."""
        self.__invoices.append(invoice)

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def calculate_progress(self) -> float:
        """Compute average progress across all milestones (Composite pattern).

        Returns:
            Float 0.0–1.0 representing overall project completion.
        """
        if not self.__milestones:
            return 0.0
        return sum(m.calculate_progress() for m in self.__milestones) / len(self.__milestones)

    def calculate_total_cost(self) -> float:
        """Sum all billable expenses for this project.

        Returns:
            Total expense amount in currency units.
        """
        return sum(e.amount for e in self.__expenses)

    def calculate_profit(self) -> float:
        """Calculate profit as budget minus total costs.

        Returns:
            budget - total_expenses.
        """
        return self.__budget - self.calculate_total_cost()

    def calculate_invoice_amount(self) -> float:
        """Delegate invoice calculation to the billing strategy.

        Returns:
            Calculated invoice amount, or 0.0 if no strategy is set.
        """
        if self.__billing_strategy is not None:
            return self.__billing_strategy.calculate_invoice(self)
        return 0.0

    def total_hours_logged(self) -> float:
        """Sum all completed hours across all tasks in all milestones.

        Returns:
            Total logged hours as a float.
        """
        total = 0.0
        for milestone in self.__milestones:
            for task in milestone.tasks:
                total += task.completed_hours
        return total

    def to_dict(self) -> dict:
        """Serialise the project to a dictionary for persistence.

        Returns:
            Dictionary mapping column names to values.
        """
        return {
            "id": self.__project_id,
            "title": self.__title,
            "description": self.__description,
            "budget": self.__budget,
            "start_date": self.__start_date,
            "deadline": self.__deadline,
            "status": self.__status,
            "billing_type": self.__billing_type,
            "billing_rate": self.__billing_rate,
            "client_id": self.__client_id,
        }

    def __repr__(self) -> str:
        return f"Project(id={self.__project_id}, title='{self.__title}')"
