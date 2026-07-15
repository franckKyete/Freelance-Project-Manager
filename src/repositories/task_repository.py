"""TaskRepository — CRUD for all Task subtypes."""

from typing import List, Optional
from src.models.task import Task
from src.factories.task_factory import TaskFactory
from ._base import get_db


class TaskRepository:
    """Handles persistence of Task objects (all subtypes)."""

    def save(self, task: Task) -> Task:
        """Insert or update a Task record."""
        db = get_db()
        d = task.to_dict()
        try:
            if task.task_id == 0:
                cursor = db.execute(
                    """
                    INSERT INTO tasks
                        (title, description, estimated_hours, completed_hours,
                         priority, status, task_type, programming_language,
                         api_type, software_used, word_target, milestone_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        d["title"], d["description"], d["estimated_hours"],
                        d["completed_hours"], d["priority"], d["status"],
                        d["task_type"], d.get("programming_language", ""),
                        d.get("api_type", ""), d.get("software_used", ""),
                        d.get("word_target", 0), d["milestone_id"],
                    ),
                )
                task.task_id = cursor.lastrowid
            else:
                db.execute(
                    """
                    UPDATE tasks
                    SET title=?, description=?, estimated_hours=?, completed_hours=?,
                        priority=?, status=?, task_type=?, programming_language=?,
                        api_type=?, software_used=?, word_target=?, milestone_id=?
                    WHERE id=?
                    """,
                    (
                        d["title"], d["description"], d["estimated_hours"],
                        d["completed_hours"], d["priority"], d["status"],
                        d["task_type"], d.get("programming_language", ""),
                        d.get("api_type", ""), d.get("software_used", ""),
                        d.get("word_target", 0), d["milestone_id"], task.task_id,
                    ),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"TaskRepository.save failed: {exc}") from exc
        return task

    def find_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve a Task by its primary key."""
        db = get_db()
        cursor = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cursor.fetchone()
        return self._row_to_task(row) if row else None

    def find_by_milestone(self, milestone_id: int) -> List[Task]:
        """Retrieve all tasks for a given milestone."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM tasks WHERE milestone_id=? ORDER BY priority DESC",
            (milestone_id,),
        )
        return [self._row_to_task(row) for row in cursor.fetchall()]

    def delete(self, task_id: int) -> bool:
        """Delete a task by primary key."""
        db = get_db()
        cursor = db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _row_to_task(row) -> Task:
        """Convert a sqlite3.Row to the correct Task subclass via TaskFactory."""
        task_type = row["task_type"] or "development"
        kwargs = dict(
            title=row["title"],
            description=row["description"],
            estimated_hours=row["estimated_hours"],
            completed_hours=row["completed_hours"],
            priority=row["priority"],
            status=row["status"],
            task_id=row["id"],
            milestone_id=row["milestone_id"] or 0,
        )
        if task_type in ("development", "backend"):
            kwargs["programming_language"] = row["programming_language"] or "Python"
        if task_type == "backend":
            api = row["api_type"] or "REST"
            from src.models.task import BackendDevelopmentTask
            if api not in BackendDevelopmentTask.API_TYPES:
                api = "REST"
            kwargs["api_type"] = api
        if task_type == "design":
            kwargs["software_used"] = row["software_used"] or "Figma"
        if task_type == "writing":
            kwargs["word_target"] = row["word_target"] or 0
        return TaskFactory.create_task(task_type, **kwargs)
