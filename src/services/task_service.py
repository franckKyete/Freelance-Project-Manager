"""TaskService — business logic for tasks and time tracking."""

from datetime import datetime
from typing import List, Optional

from src.models.task import Task
from src.models.time_entry import TimeEntry
from src.factories.task_factory import TaskFactory
from src.repositories.task_repository import TaskRepository
from src.repositories.time_entry_repository import TimeEntryRepository
from src.exceptions.app_exceptions import InvalidTaskException


class TaskService:
    """Business logic for creating, updating, and tracking tasks."""

    def __init__(self) -> None:
        self._task_repo = TaskRepository()
        self._time_repo = TimeEntryRepository()

    def create_task(self, task_type: str, milestone_id: int, **kwargs) -> Task:
        """Create and save a new task via the TaskFactory.

        Args:
            task_type: One of 'development', 'backend', 'design', 'writing'.
            milestone_id: FK of the owning milestone.
            **kwargs: Field values forwarded to TaskFactory.create_task().

        Returns:
            The saved Task.

        Raises:
            InvalidTaskException: If task_type or kwargs are invalid.
        """
        try:
            kwargs["milestone_id"] = milestone_id
            task = TaskFactory.create_task(task_type, **kwargs)
            return self._task_repo.save(task)
        except InvalidTaskException:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to create task: {exc}") from exc

    def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        return self._task_repo.save(task)

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed.

        Args:
            task_id: The task's database id.

        Returns:
            The updated Task.
        """
        task = self._task_repo.find_by_id(task_id)
        if task is None:
            raise InvalidTaskException(f"Task id={task_id} not found.")
        try:
            task.complete()
            self._task_repo.save(task)
        except InvalidTaskException:
            raise
        else:
            return task
        finally:
            pass  # logging hook

    def delete_task(self, task_id: int) -> None:
        """Delete a task."""
        self._task_repo.delete(task_id)

    def get_tasks_for_milestone(self, milestone_id: int) -> List[Task]:
        """Return all tasks for a given milestone."""
        return self._task_repo.find_by_milestone(milestone_id)

    # ------------------------------------------------------------------ #
    # Time tracking
    # ------------------------------------------------------------------ #

    def log_time(
        self,
        task_id: int,
        start_time: str,
        end_time: str,
        duration: float = 0.0,
    ) -> TimeEntry:
        """Log a completed work session.

        Args:
            task_id: FK of the owning task.
            start_time: ISO datetime string.
            end_time: ISO datetime string.
            duration: Override duration in hours (computed if 0).

        Returns:
            The saved TimeEntry.
        """
        try:
            entry = TimeEntry(task_id=task_id, start_time=start_time, end_time=end_time)
            if duration > 0:
                entry.duration = duration
            saved_entry = self._time_repo.save(entry)

            # Update task's completed_hours
            task = self._task_repo.find_by_id(task_id)
            if task:
                task.completed_hours = task.completed_hours + saved_entry.duration
                self._task_repo.save(task)

            return saved_entry
        except Exception as exc:
            raise RuntimeError(f"Failed to log time: {exc}") from exc

    def get_time_entries(self, task_id: int) -> List[TimeEntry]:
        """Return all time entries for a task."""
        return self._time_repo.find_by_task(task_id)

    def delete_time_entry(self, entry_id: int) -> None:
        """Delete a time entry."""
        self._time_repo.delete(entry_id)
