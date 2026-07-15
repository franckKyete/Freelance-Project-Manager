"""TimeEntry model — records a single work session on a task."""

from datetime import datetime


class TimeEntry:
    """Represents one logged work session.

    Attributes (private):
        __entry_id: Database primary key.
        __task_id: FK of the task this session belongs to.
        __start_time: ISO 8601 start datetime string.
        __end_time: ISO 8601 end datetime string.
        __duration: Duration in hours (computed or manually set).
    """

    DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        task_id: int,
        start_time: str = "",
        end_time: str = "",
        duration: float = 0.0,
        entry_id: int = 0,
    ) -> None:
        """Initialise a TimeEntry.

        Args:
            task_id: FK of the owning task.
            start_time: ISO 8601 start datetime string.
            end_time: ISO 8601 end datetime string (empty if still running).
            duration: Hours logged; auto-calculated if start and end are provided.
            entry_id: Database primary key.
        """
        self.__entry_id: int = entry_id
        self.__task_id: int = task_id
        self.__start_time: str = start_time
        self.__end_time: str = end_time
        self.__duration: float = float(duration)

        # Auto-compute duration when both timestamps are available.
        if start_time and end_time and duration == 0.0:
            self.__duration = self.calculate_duration()

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def entry_id(self) -> int:
        """int: Database primary key."""
        return self.__entry_id

    @entry_id.setter
    def entry_id(self, value: int) -> None:
        self.__entry_id = int(value)

    @property
    def task_id(self) -> int:
        """int: FK of the owning task."""
        return self.__task_id

    @task_id.setter
    def task_id(self, value: int) -> None:
        self.__task_id = int(value)

    @property
    def start_time(self) -> str:
        """str: ISO 8601 start datetime."""
        return self.__start_time

    @start_time.setter
    def start_time(self, value: str) -> None:
        self.__start_time = value.strip()

    @property
    def end_time(self) -> str:
        """str: ISO 8601 end datetime."""
        return self.__end_time

    @end_time.setter
    def end_time(self, value: str) -> None:
        self.__end_time = value.strip()

    @property
    def duration(self) -> float:
        """float: Session length in hours."""
        return self.__duration

    @duration.setter
    def duration(self, value: float) -> None:
        if value < 0:
            raise ValueError("duration cannot be negative.")
        self.__duration = float(value)

    # ------------------------------------------------------------------ #
    # Business methods
    # ------------------------------------------------------------------ #

    def calculate_duration(self) -> float:
        """Compute duration in hours from start and end timestamps.

        Returns:
            Number of hours between start_time and end_time.
            Returns 0.0 if either timestamp is missing or unparseable.
        """
        try:
            start = datetime.strptime(self.__start_time, self.DATETIME_FMT)
            end = datetime.strptime(self.__end_time, self.DATETIME_FMT)
            delta = end - start
            return max(delta.total_seconds() / 3600, 0.0)
        except (ValueError, TypeError):
            return 0.0

    def to_dict(self) -> dict:
        """Serialise the time entry to a dictionary.

        Returns:
            Dictionary mapping column names to values.
        """
        return {
            "id": self.__entry_id,
            "task_id": self.__task_id,
            "start_time": self.__start_time,
            "end_time": self.__end_time,
            "duration": self.__duration,
        }

    def __repr__(self) -> str:
        return (
            f"TimeEntry(id={self.__entry_id}, task_id={self.__task_id}, "
            f"duration={self.__duration:.2f}h)"
        )
