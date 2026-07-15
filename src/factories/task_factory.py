"""TaskFactory — Factory design pattern for creating Task instances.

Design Pattern: **Factory**
Centralises the creation of all Task subclasses so calling code never
needs to import or instantiate concrete Task classes directly.

Example:
    task = TaskFactory.create_task("backend", title="Build REST API",
                                   programming_language="Python",
                                   api_type="REST")
"""

from src.models.task import (
    Task,
    DevelopmentTask,
    BackendDevelopmentTask,
    DesignTask,
    WritingTask,
)
from src.exceptions.app_exceptions import InvalidTaskException


# Registry of known task types
TASK_TYPE_MAP = {
    "development": DevelopmentTask,
    "backend": BackendDevelopmentTask,
    "design": DesignTask,
    "writing": WritingTask,
}


class TaskFactory:
    """Factory class responsible for creating Task instances.

    All instantiation of concrete Task subclasses should go through
    this factory.  This decouples the caller from the concrete types
    and makes it easy to add new task types in the future.
    """

    @staticmethod
    def create_task(task_type: str, **kwargs) -> Task:
        """Create and return the appropriate Task subclass instance.

        Args:
            task_type: One of 'development', 'backend', 'design', 'writing'.
            **kwargs: Keyword arguments forwarded to the Task constructor.
                Common kwargs for all types:
                    title (str): Task title (required).
                    description (str): Detailed description.
                    estimated_hours (float): Planned effort.
                    completed_hours (float): Hours already logged.
                    priority (str): 'low' | 'medium' | 'high' | 'critical'.
                    status (str): 'todo' | 'in_progress' | 'review' | 'done'.
                    task_id (int): Database primary key.
                    milestone_id (int): FK of the owning milestone.
                Type-specific kwargs:
                    programming_language (str): For 'development' / 'backend'.
                    api_type (str): For 'backend' only.
                    software_used (str): For 'design' only.
                    word_target (int): For 'writing' only.

        Returns:
            An instance of the correct Task subclass.

        Raises:
            InvalidTaskException: If task_type is not recognised or if
                                  required kwargs are missing.
        """
        task_type = task_type.lower().strip()
        cls = TASK_TYPE_MAP.get(task_type)

        if cls is None:
            raise InvalidTaskException(
                f"Unknown task type '{task_type}'. "
                f"Valid types are: {list(TASK_TYPE_MAP.keys())}"
            )

        try:
            return cls(**kwargs)
        except (TypeError, ValueError) as exc:
            raise InvalidTaskException(
                f"Failed to create task of type '{task_type}': {exc}"
            ) from exc

    @staticmethod
    def available_types() -> list:
        """Return a list of supported task type identifiers.

        Returns:
            List of strings: ['development', 'backend', 'design', 'writing'].
        """
        return list(TASK_TYPE_MAP.keys())
