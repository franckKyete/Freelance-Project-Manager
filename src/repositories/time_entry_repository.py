"""TimeEntryRepository — CRUD for TimeEntry entities."""

from typing import List, Optional
from src.models.time_entry import TimeEntry
from ._base import get_db


class TimeEntryRepository:
    """Handles persistence of TimeEntry objects."""

    def save(self, entry: TimeEntry) -> TimeEntry:
        """Insert or update a TimeEntry record."""
        db = get_db()
        try:
            if entry.entry_id == 0:
                cursor = db.execute(
                    "INSERT INTO time_entries (task_id, start_time, end_time, duration) VALUES (?, ?, ?, ?)",
                    (entry.task_id, entry.start_time, entry.end_time, entry.duration),
                )
                entry.entry_id = cursor.lastrowid
            else:
                db.execute(
                    "UPDATE time_entries SET task_id=?, start_time=?, end_time=?, duration=? WHERE id=?",
                    (entry.task_id, entry.start_time, entry.end_time, entry.duration, entry.entry_id),
                )
            db.commit()
        except Exception as exc:
            raise RuntimeError(f"TimeEntryRepository.save failed: {exc}") from exc
        return entry

    def find_by_task(self, task_id: int) -> List[TimeEntry]:
        """Retrieve all time entries for a given task."""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM time_entries WHERE task_id=? ORDER BY start_time DESC",
            (task_id,),
        )
        return [self._row_to_entry(row) for row in cursor.fetchall()]

    def delete(self, entry_id: int) -> bool:
        """Delete a time entry by primary key."""
        db = get_db()
        cursor = db.execute("DELETE FROM time_entries WHERE id=?", (entry_id,))
        db.commit()
        return cursor.rowcount > 0

    def total_hours_this_week(self) -> float:
        """Calculate total hours logged in the current ISO week."""
        db = get_db()
        cursor = db.execute(
            """
            SELECT COALESCE(SUM(duration), 0) AS total
            FROM time_entries
            WHERE strftime('%W', start_time) = strftime('%W', 'now')
              AND strftime('%Y', start_time) = strftime('%Y', 'now')
            """
        )
        row = cursor.fetchone()
        return float(row["total"]) if row else 0.0

    @staticmethod
    def _row_to_entry(row) -> TimeEntry:
        return TimeEntry(
            task_id=row["task_id"] or 0,
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration=row["duration"],
            entry_id=row["id"],
        )
