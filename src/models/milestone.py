"""Milestone model — contains Tasks (Composite pattern node)."""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task

STATUS_OPTIONS = ("pending", "in_progress", "completed")


class Milestone:
    """A project milestone that groups related tasks.

    Design Pattern: **Composite** — intermediate node.
    Progress is calculated from its child tasks and propagated upward to Project.

    Attributes (private):
        __milestone_id: Database primary key.
        __project_id: Foreign key of the owning project.
        __title: Milestone title.
        __due_date: Target completion date (ISO 8601 string).
        __status: Current status string.
        __tasks: List of Task objects belonging to this milestone.
    """

    def __init__(
        self,
        title: str,
        due_date: str = "",
        status: str = "pending",
        project_id: int = 0,
        milestone_id: int = 0,
    ) -> None:
        """Initialise a Milestone.

        Args:
            title: Milestone title (non-empty).
            due_date: ISO 8601 date string (e.g. '2025-12-31').
            status: One of 'pending', 'in_progress', 'completed'.
            project_id: FK of the owning project.
            milestone_id: Database primary key.

        Raises:
            ValueError: If title is empty or status is invalid.
        """
        self.__milestone_id: int = milestone_id
        self.__project_id: int = project_id
        self.title = title      # setter validates
        self.__due_date: str = due_date
        self.status = status    # setter validates
        self.__tasks: List["Task"] = []

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def milestone_id(self) -> int:
        """int: Database primary key."""
        return self.__milestone_id

    @milestone_id.setter
    def milestone_id(self, value: int) -> None:
        self.__milestone_id = int(value)

    @property
    def project_id(self) -> int:
        """int: FK of the owning project."""
        return self.__project_id

    @project_id.setter
    def project_id(self, value: int) -> None:
        self.__project_id = int(value)

    @property
    def title(self) -> str:
        """str: Milestone title."""
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("Milestone title cannot be empty.")
        self.__title = value

    @property
    def due_date(self) -> str:
        """str: ISO 8601 target completion date."""
        return self.__due_date

    @due_date.setter
    def due_date(self, value: str) -> None:
        self.__due_date = value.strip()

    @property
    def status(self) -> str:
        """str: Current milestone status."""
        return self.__status

    @status.setter
    def status(self, value: str) -> None:
        value = value.lower().strip()
        if value not in STATUS_OPTIONS:
            raise ValueError(f"Milestone status must be one of {STATUS_OPTIONS}.")
        self.__status = value

    @property
    def tasks(self) -> List["Task"]:
        """List[Task]: Read-only view of the milestone's tasks."""
        return list(self.__tasks)

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def add_task(self, task: "Task") -> None:
        """Add a task to this milestone.

        Args:
            task: The Task to add.

        Raises:
            TypeError: If task is not a Task instance.
        """
        from .task import Task  # avoid circular import
        if not isinstance(task, Task):
            raise TypeError("Only Task instances can be added to a Milestone.")
        self.__tasks.append(task)

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by its id.

        Args:
            task_id: Database id of the task to remove.

        Returns:
            True if a task was removed, False otherwise.
        """
        original_len = len(self.__tasks)
        self.__tasks = [t for t in self.__tasks if t.task_id != task_id]
        return len(self.__tasks) < original_len

    def calculate_progress(self) -> float:
        """Compute the average progress of all tasks (Composite pattern).

        Returns:
            Float from 0.0 to 1.0 representing overall milestone completion.
            Returns 0.0 if there are no tasks.
        """
        if not self.__tasks:
            return 0.0
        return sum(t.get_progress() for t in self.__tasks) / len(self.__tasks)

    def to_dict(self) -> dict:
        """Serialise the milestone to a dictionary for persistence.

        Returns:
            Dictionary mapping column names to values.
        """
        return {
            "id": self.__milestone_id,
            "title": self.__title,
            "due_date": self.__due_date,
            "status": self.__status,
            "project_id": self.__project_id,
        }

    def __repr__(self) -> str:
        return f"Milestone(id={self.__milestone_id}, title='{self.__title}')"
