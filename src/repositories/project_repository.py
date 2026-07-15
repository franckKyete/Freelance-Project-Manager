"""ProjectRepository — CRUD operations for Project entities."""

from typing import List, Optional
from src.models.project import Project
from ._base import get_db


class ProjectRepository:
    """Handles persistence of Project objects."""

    def save(self, project: Project) -> Project:
        """Insert or update a Project record."""
        db = get_db()
        try:
            if project.project_id == 0:
                cursor = db.execute(
                    """
                    INSERT INTO projects
                        (title, description, budget, start_date, deadline,
                         status, billing_type, billing_rate, client_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project.title, project.description, project.budget,
                        project.start_date, project.deadline, project.status,
                        project.billing_type, project.billing_rate, project.client_id,
                    ),
                )
                project.project_id = cursor.lastrowid
            else:
                db.execute(
                    """
                    UPDATE projects
                    SET title=?, description=?, budget=?, start_date=?, deadline=?,
                        status=?, billing_type=?, billing_rate=?, client_id=?
                    WHERE id=?
                    """,
                    (
                        project.title, project.description, project.budget,
                        project.start_date, project.deadline, project.status,
                        project.billing_type, project.billing_rate,
                        project.client_id, project.project_id,
                    ),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"ProjectRepository.save failed: {exc}") from exc
        return project

    def find_by_id(self, project_id: int) -> Optional[Project]:
        """Retrieve a Project by its primary key."""
        db = get_db()
        cursor = db.execute("SELECT * FROM projects WHERE id=?", (project_id,))
        row = cursor.fetchone()
        return self._row_to_project(row) if row else None

    def find_all(self) -> List[Project]:
        """Retrieve all projects ordered by title."""
        db = get_db()
        cursor = db.execute("SELECT * FROM projects ORDER BY title")
        return [self._row_to_project(row) for row in cursor.fetchall()]

    def find_by_client(self, client_id: int) -> List[Project]:
        """Retrieve all projects for a given client."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM projects WHERE client_id=? ORDER BY title",
            (client_id,),
        )
        return [self._row_to_project(row) for row in cursor.fetchall()]

    def find_active(self) -> List[Project]:
        """Retrieve all active projects."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM projects WHERE status='active' ORDER BY deadline"
        )
        return [self._row_to_project(row) for row in cursor.fetchall()]

    def delete(self, project_id: int) -> bool:
        """Delete a project by primary key."""
        db = get_db()
        cursor = db.execute("DELETE FROM projects WHERE id=?", (project_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _row_to_project(row) -> Project:
        """Convert a sqlite3.Row to a Project instance."""
        return Project(
            title=row["title"],
            client_id=row["client_id"] or 0,
            description=row["description"],
            budget=row["budget"],
            start_date=row["start_date"],
            deadline=row["deadline"],
            status=row["status"],
            billing_type=row["billing_type"],
            billing_rate=row["billing_rate"],
            project_id=row["id"],
        )
