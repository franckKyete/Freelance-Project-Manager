"""MilestoneRepository — CRUD for Milestone entities."""

from typing import List, Optional
from src.models.milestone import Milestone
from ._base import get_db


class MilestoneRepository:
    """Handles persistence of Milestone objects."""

    def save(self, milestone: Milestone) -> Milestone:
        """Insert or update a Milestone record."""
        db = get_db()
        try:
            if milestone.milestone_id == 0:
                cursor = db.execute(
                    "INSERT INTO milestones (title, due_date, status, project_id) VALUES (?, ?, ?, ?)",
                    (milestone.title, milestone.due_date, milestone.status, milestone.project_id),
                )
                milestone.milestone_id = cursor.lastrowid
            else:
                db.execute(
                    "UPDATE milestones SET title=?, due_date=?, status=?, project_id=? WHERE id=?",
                    (milestone.title, milestone.due_date, milestone.status,
                     milestone.project_id, milestone.milestone_id),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"MilestoneRepository.save failed: {exc}") from exc
        return milestone

    def find_by_id(self, milestone_id: int) -> Optional[Milestone]:
        """Retrieve a Milestone by its primary key."""
        db = get_db()
        cursor = db.execute("SELECT * FROM milestones WHERE id=?", (milestone_id,))
        row = cursor.fetchone()
        return self._row_to_milestone(row) if row else None

    def find_by_project(self, project_id: int) -> List[Milestone]:
        """Retrieve all milestones for a given project."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM milestones WHERE project_id=? ORDER BY due_date",
            (project_id,),
        )
        return [self._row_to_milestone(row) for row in cursor.fetchall()]

    def delete(self, milestone_id: int) -> bool:
        """Delete a milestone by primary key."""
        db = get_db()
        cursor = db.execute("DELETE FROM milestones WHERE id=?", (milestone_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _row_to_milestone(row) -> Milestone:
        return Milestone(
            title=row["title"],
            due_date=row["due_date"],
            status=row["status"],
            project_id=row["project_id"] or 0,
            milestone_id=row["id"],
        )
