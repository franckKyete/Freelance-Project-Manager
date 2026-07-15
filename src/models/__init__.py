"""Models package — domain entities for the Freelance Project Manager."""

from .person import Person, Freelancer, SeniorFreelancer
from .client import Client
from .project import Project
from .milestone import Milestone
from .task import Task, DevelopmentTask, BackendDevelopmentTask, DesignTask, WritingTask
from .time_entry import TimeEntry
from .expense import Expense
from .invoice import Invoice

__all__ = [
    "Person", "Freelancer", "SeniorFreelancer",
    "Client",
    "Project",
    "Milestone",
    "Task", "DevelopmentTask", "BackendDevelopmentTask", "DesignTask", "WritingTask",
    "TimeEntry",
    "Expense",
    "Invoice",
]
