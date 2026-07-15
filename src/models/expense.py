"""Expense model — tracks project-related costs."""

EXPENSE_CATEGORIES = (
    "General", "Software", "Hardware", "Travel",
    "Communication", "Hosting", "Marketing", "Other"
)


class Expense:
    """Represents a single expense associated with a project.

    Attributes (private):
        __expense_id: Database primary key.
        __project_id: FK of the owning project.
        __category: Expense category string.
        __description: Short description of the expense.
        __amount: Expense amount in currency units (>= 0).
        __date: ISO 8601 date string.
        __billable: Whether this expense can be charged to the client.
    """

    def __init__(
        self,
        project_id: int,
        amount: float,
        category: str = "General",
        description: str = "",
        date: str = "",
        billable: bool = False,
        expense_id: int = 0,
    ) -> None:
        """Initialise an Expense.

        Args:
            project_id: FK of the owning project.
            amount: Expense amount (must be >= 0).
            category: One of EXPENSE_CATEGORIES.
            description: Short description.
            date: ISO 8601 date string (e.g. '2025-06-15').
            billable: True if this should be passed on to the client.
            expense_id: Database primary key.

        Raises:
            ValueError: If amount is negative.
        """
        self.__expense_id: int = expense_id
        self.__project_id: int = project_id
        self.amount = amount        # setter validates
        self.__category: str = category
        self.__description: str = description
        self.__date: str = date
        self.__billable: bool = bool(billable)

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def expense_id(self) -> int:
        """int: Database primary key."""
        return self.__expense_id

    @expense_id.setter
    def expense_id(self, value: int) -> None:
        self.__expense_id = int(value)

    @property
    def project_id(self) -> int:
        """int: FK of the owning project."""
        return self.__project_id

    @project_id.setter
    def project_id(self, value: int) -> None:
        self.__project_id = int(value)

    @property
    def category(self) -> str:
        """str: Expense category."""
        return self.__category

    @category.setter
    def category(self, value: str) -> None:
        self.__category = value.strip()

    @property
    def description(self) -> str:
        """str: Short description of the expense."""
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value.strip()

    @property
    def amount(self) -> float:
        """float: Expense amount (must be >= 0)."""
        return self.__amount

    @amount.setter
    def amount(self, value: float) -> None:
        if value < 0:
            raise ValueError("Expense amount cannot be negative.")
        self.__amount = float(value)

    @property
    def date(self) -> str:
        """str: ISO 8601 expense date."""
        return self.__date

    @date.setter
    def date(self, value: str) -> None:
        self.__date = value.strip()

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def is_billable(self) -> bool:
        """Return whether this expense should be billed to the client.

        Returns:
            True if the expense is marked as billable.
        """
        return self.__billable

    def set_billable(self, value: bool) -> None:
        """Set the billable flag.

        Args:
            value: True to mark as billable, False otherwise.
        """
        self.__billable = bool(value)

    def to_dict(self) -> dict:
        """Serialise the expense to a dictionary for persistence.

        Returns:
            Dictionary mapping column names to values.
        """
        return {
            "id": self.__expense_id,
            "project_id": self.__project_id,
            "category": self.__category,
            "description": self.__description,
            "amount": self.__amount,
            "date": self.__date,
            "billable": int(self.__billable),
        }

    def __repr__(self) -> str:
        return (
            f"Expense(id={self.__expense_id}, amount={self.__amount:.2f}, "
            f"category='{self.__category}')"
        )
