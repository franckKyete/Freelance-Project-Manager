"""Task abstract base class and concrete task types.

Inheritance chains (2nd 3-level chain):
    Task (ABC) → DevelopmentTask → BackendDevelopmentTask
    Task (ABC) → DesignTask
    Task (ABC) → WritingTask
"""

from abc import ABC, abstractmethod
from typing import List

PRIORITY_LEVELS = ("low", "medium", "high", "critical")
STATUS_OPTIONS = ("todo", "in_progress", "review", "done")


class Task(ABC):
    """Abstract base class representing a unit of work within a milestone.

    Design Pattern contribution: **Composite** leaf node.
    Design Pattern contribution: **Factory** product.

    Attributes (private):
        __title: Short title of the task.
        __description: Detailed description.
        __estimated_hours: Planned effort in hours.
        __completed_hours: Actual hours logged.
        __priority: One of PRIORITY_LEVELS.
        __status: One of STATUS_OPTIONS.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        estimated_hours: float = 0.0,
        completed_hours: float = 0.0,
        priority: str = "medium",
        status: str = "todo",
        task_id: int = 0,
        milestone_id: int = 0,
    ) -> None:
        """Initialise a Task.

        Args:
            title: Short name of the task (non-empty).
            description: Detailed description.
            estimated_hours: Planned hours (>= 0).
            completed_hours: Hours already logged (>= 0).
            priority: One of 'low', 'medium', 'high', 'critical'.
            status: One of 'todo', 'in_progress', 'review', 'done'.
            task_id: Database primary key.
            milestone_id: Foreign key of the owning milestone.

        Raises:
            ValueError: If title is empty, hours negative, or enums invalid.
        """
        self.__task_id: int = task_id
        self.__milestone_id: int = milestone_id
        self.title = title                          # setter validates
        self.__description: str = description
        self.estimated_hours = estimated_hours      # setter validates
        self.completed_hours = completed_hours      # setter validates
        self.priority = priority                    # setter validates
        self.status = status                        # setter validates

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def task_id(self) -> int:
        """int: Database primary key."""
        return self.__task_id

    @task_id.setter
    def task_id(self, value: int) -> None:
        self.__task_id = int(value)

    @property
    def milestone_id(self) -> int:
        """int: FK of the owning milestone."""
        return self.__milestone_id

    @milestone_id.setter
    def milestone_id(self, value: int) -> None:
        self.__milestone_id = int(value)

    @property
    def title(self) -> str:
        """str: Task title."""
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be empty.")
        self.__title = value

    @property
    def description(self) -> str:
        """str: Detailed task description."""
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value

    @property
    def estimated_hours(self) -> float:
        """float: Planned effort in hours."""
        return self.__estimated_hours

    @estimated_hours.setter
    def estimated_hours(self, value: float) -> None:
        if value < 0:
            raise ValueError("estimated_hours cannot be negative.")
        self.__estimated_hours = float(value)

    @property
    def completed_hours(self) -> float:
        """float: Actual hours logged so far."""
        return self.__completed_hours

    @completed_hours.setter
    def completed_hours(self, value: float) -> None:
        if value < 0:
            raise ValueError("completed_hours cannot be negative.")
        self.__completed_hours = float(value)

    @property
    def priority(self) -> str:
        """str: Task priority level."""
        return self.__priority

    @priority.setter
    def priority(self, value: str) -> None:
        value = value.lower().strip()
        if value not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {PRIORITY_LEVELS}.")
        self.__priority = value

    @property
    def status(self) -> str:
        """str: Current task status."""
        return self.__status

    @status.setter
    def status(self, value: str) -> None:
        value = value.lower().strip()
        if value not in STATUS_OPTIONS:
            raise ValueError(f"status must be one of {STATUS_OPTIONS}.")
        self.__status = value

    # ------------------------------------------------------------------ #
    # Abstract methods
    # ------------------------------------------------------------------ #

    @abstractmethod
    def calculate_cost(self, hourly_rate: float) -> float:
        """Calculate the billable cost of this task.

        Args:
            hourly_rate: The rate to apply per logged hour.

        Returns:
            Total billable amount for this task.
        """

    @abstractmethod
    def complete(self) -> None:
        """Mark the task as completed and perform any subclass-specific logic."""

    # ------------------------------------------------------------------ #
    # Concrete methods
    # ------------------------------------------------------------------ #

    def get_progress(self) -> float:
        """Return the completion ratio (0.0 – 1.0).

        Returns:
            Ratio of completed_hours to estimated_hours.
            Returns 1.0 if the task status is 'done' or if estimated_hours == 0.
        """
        if self.__status == "done":
            return 1.0
        if self.__estimated_hours == 0:
            return 0.0
        return min(self.__completed_hours / self.__estimated_hours, 1.0)

    def to_dict(self) -> dict:
        """Return a plain dictionary suitable for database persistence.

        Subclasses should call super().to_dict() and extend the result.

        Returns:
            Dictionary of field names → values.
        """
        return {
            "id": self.__task_id,
            "title": self.__title,
            "description": self.__description,
            "estimated_hours": self.__estimated_hours,
            "completed_hours": self.__completed_hours,
            "priority": self.__priority,
            "status": self.__status,
            "milestone_id": self.__milestone_id,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.__task_id}, title='{self.__title}')"


# ====================================================================== #
# DevelopmentTask  (Task → DevelopmentTask)                               #
# ====================================================================== #

class DevelopmentTask(Task):
    """A software development task.

    Inherits from Task and adds a programming_language attribute.

    Attributes (private):
        __programming_language: The language used for this task.
    """

    TASK_TYPE = "development"

    def __init__(
        self,
        title: str,
        programming_language: str = "Python",
        description: str = "",
        estimated_hours: float = 0.0,
        completed_hours: float = 0.0,
        priority: str = "medium",
        status: str = "todo",
        task_id: int = 0,
        milestone_id: int = 0,
    ) -> None:
        """Initialise a DevelopmentTask.

        Args:
            title: Task title.
            programming_language: Language used (e.g. 'Python', 'JavaScript').
            description: Detailed description.
            estimated_hours: Planned hours.
            completed_hours: Hours already logged.
            priority: Priority level.
            status: Current status.
            task_id: Database PK.
            milestone_id: Parent milestone FK.
        """
        super().__init__(
            title, description, estimated_hours,
            completed_hours, priority, status, task_id, milestone_id
        )
        self.__programming_language: str = programming_language.strip()

    @property
    def programming_language(self) -> str:
        """str: Programming language for this development task."""
        return self.__programming_language

    @programming_language.setter
    def programming_language(self, value: str) -> None:
        self.__programming_language = value.strip()

    # ------------------------------------------------------------------ #
    # Abstract method implementations
    # ------------------------------------------------------------------ #

    def calculate_cost(self, hourly_rate: float) -> float:
        """Calculate cost based on completed hours and hourly rate.

        Args:
            hourly_rate: Billing rate per hour.

        Returns:
            completed_hours × hourly_rate.
        """
        return self.completed_hours * hourly_rate

    def complete(self) -> None:
        """Mark the task as done and set completed_hours to estimated_hours if zero."""
        self.status = "done"
        if self.completed_hours == 0 and self.estimated_hours > 0:
            self.completed_hours = self.estimated_hours

    def to_dict(self) -> dict:
        """Extend parent dict with development-specific fields."""
        data = super().to_dict()
        data["task_type"] = self.TASK_TYPE
        data["programming_language"] = self.__programming_language
        data["api_type"] = ""
        data["software_used"] = ""
        data["word_target"] = 0
        return data


# ====================================================================== #
# BackendDevelopmentTask  (Task → DevelopmentTask → BackendDevelopmentTask)
# ====================================================================== #

class BackendDevelopmentTask(DevelopmentTask):
    """A backend-specific development task.

    Inherits from DevelopmentTask and adds api_type to distinguish
    REST, GraphQL, and gRPC architectures.

    This class provides the **3rd inheritance level** required by the exam.

    Attributes (private):
        __api_type: One of 'REST', 'GraphQL', 'gRPC', 'WebSocket', 'Other'.
    """

    TASK_TYPE = "backend"
    API_TYPES = ("REST", "GraphQL", "gRPC", "WebSocket", "Other")

    def __init__(
        self,
        title: str,
        programming_language: str = "Python",
        api_type: str = "REST",
        description: str = "",
        estimated_hours: float = 0.0,
        completed_hours: float = 0.0,
        priority: str = "medium",
        status: str = "todo",
        task_id: int = 0,
        milestone_id: int = 0,
    ) -> None:
        """Initialise a BackendDevelopmentTask.

        Args:
            title: Task title.
            programming_language: Language used.
            api_type: API architecture type.
            description: Detailed description.
            estimated_hours: Planned hours.
            completed_hours: Hours already logged.
            priority: Priority level.
            status: Current status.
            task_id: Database PK.
            milestone_id: Parent milestone FK.

        Raises:
            ValueError: If api_type is not in API_TYPES.
        """
        super().__init__(
            title, programming_language, description,
            estimated_hours, completed_hours, priority, status, task_id, milestone_id
        )
        self.api_type = api_type  # uses setter

    @property
    def api_type(self) -> str:
        """str: API architecture type for this backend task."""
        return self.__api_type

    @api_type.setter
    def api_type(self, value: str) -> None:
        if value not in self.API_TYPES:
            raise ValueError(f"api_type must be one of {self.API_TYPES}.")
        self.__api_type = value

    # ------------------------------------------------------------------ #
    # Overridden method (method overriding at the 3rd level)
    # ------------------------------------------------------------------ #

    def calculate_cost(self, hourly_rate: float) -> float:
        """Calculate cost with a 10 % backend complexity premium.

        Overrides DevelopmentTask.calculate_cost().

        Args:
            hourly_rate: Base billing rate per hour.

        Returns:
            completed_hours × hourly_rate × 1.10.
        """
        base_cost = super().calculate_cost(hourly_rate)
        return base_cost * 1.10  # 10% backend complexity surcharge

    def complete(self) -> None:
        """Mark the backend task as done and log a completion note."""
        super().complete()
        # Additional backend-specific completion logic could go here.

    def to_dict(self) -> dict:
        """Extend parent dict with backend-specific fields."""
        data = super().to_dict()
        data["task_type"] = self.TASK_TYPE
        data["api_type"] = self.__api_type
        return data


# ====================================================================== #
# DesignTask  (Task → DesignTask)                                          #
# ====================================================================== #

class DesignTask(Task):
    """A UI/UX or graphic design task.

    Attributes (private):
        __software_used: Design tool used (e.g. 'Figma', 'Adobe XD').
    """

    TASK_TYPE = "design"

    def __init__(
        self,
        title: str,
        software_used: str = "Figma",
        description: str = "",
        estimated_hours: float = 0.0,
        completed_hours: float = 0.0,
        priority: str = "medium",
        status: str = "todo",
        task_id: int = 0,
        milestone_id: int = 0,
    ) -> None:
        super().__init__(
            title, description, estimated_hours,
            completed_hours, priority, status, task_id, milestone_id
        )
        self.__software_used: str = software_used.strip()

    @property
    def software_used(self) -> str:
        """str: Design software used for this task."""
        return self.__software_used

    @software_used.setter
    def software_used(self, value: str) -> None:
        self.__software_used = value.strip()

    def calculate_cost(self, hourly_rate: float) -> float:
        """Calculate cost based on completed hours.

        Design tasks use a flat rate (no surcharge).

        Args:
            hourly_rate: Billing rate per hour.

        Returns:
            completed_hours × hourly_rate.
        """
        return self.completed_hours * hourly_rate

    def complete(self) -> None:
        """Mark the design task as done."""
        self.status = "done"
        if self.completed_hours == 0 and self.estimated_hours > 0:
            self.completed_hours = self.estimated_hours

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["task_type"] = self.TASK_TYPE
        data["software_used"] = self.__software_used
        data["programming_language"] = ""
        data["api_type"] = ""
        data["word_target"] = 0
        return data


# ====================================================================== #
# WritingTask  (Task → WritingTask)                                        #
# ====================================================================== #

class WritingTask(Task):
    """A content writing or documentation task.

    Attributes (private):
        __word_target: Target word count for the deliverable.
    """

    TASK_TYPE = "writing"

    def __init__(
        self,
        title: str,
        word_target: int = 0,
        description: str = "",
        estimated_hours: float = 0.0,
        completed_hours: float = 0.0,
        priority: str = "medium",
        status: str = "todo",
        task_id: int = 0,
        milestone_id: int = 0,
    ) -> None:
        super().__init__(
            title, description, estimated_hours,
            completed_hours, priority, status, task_id, milestone_id
        )
        self.word_target = word_target  # uses setter

    @property
    def word_target(self) -> int:
        """int: Target word count for the writing deliverable."""
        return self.__word_target

    @word_target.setter
    def word_target(self, value: int) -> None:
        if value < 0:
            raise ValueError("word_target must be >= 0.")
        self.__word_target = int(value)

    def calculate_cost(self, hourly_rate: float) -> float:
        """Calculate writing task cost.

        Writing tasks are billed purely on time spent.

        Args:
            hourly_rate: Billing rate per hour.

        Returns:
            completed_hours × hourly_rate.
        """
        return self.completed_hours * hourly_rate

    def complete(self) -> None:
        """Mark the writing task as done."""
        self.status = "done"
        if self.completed_hours == 0 and self.estimated_hours > 0:
            self.completed_hours = self.estimated_hours

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["task_type"] = self.TASK_TYPE
        data["word_target"] = self.__word_target
        data["programming_language"] = ""
        data["api_type"] = ""
        data["software_used"] = ""
        return data
