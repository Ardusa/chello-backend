from datetime import datetime, timedelta

from pydantic import BaseModel
from enum import Enum
from prioritization_engine import calculate_time_estimate, calculate_time_of_completion, calculate_efficiency
from typing import Optional, List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TaskStatus(Enum):
    """Working status of task."""

    OPEN = "OPEN"
    """Task is open and ready to be started."""
    IN_PROGRESS = "IN_PROGRESS"
    """Task is currently being worked on."""
    COMPLETED = "COMPLETED"
    """Task has been completed."""


class Employee(BaseModel):
    """Employee model to store employee details."""

    id: str
    """Unique identifier for the employee (username or employee ID)."""
    full_name: str
    """Full name of the employee."""
    email: str
    """Email address of the employee."""
    position: Optional[int] = 1
    """Position of the employee in the organization, 1 for base level, 2 for manager, 3 for admin."""
    enabled: Optional[bool] = True
    """Flag to enable or disable the employee account."""
    efficiency_score: Optional[float] = 1.0  # Default efficiency score of 100%
    """Efficiency score of the employee (default: 100%)."""
    password: str = "password"
    """Password for the employee account."""

    def __init__(self, **data):
        super().__init__(**data)
        self.password = pwd_context.hash(self.password)


class Task(BaseModel):
    """Task model to store task details."""

    name: str
    """Name of the task."""
    description: str
    """Description of the task."""
    dependencies: List[str] = []
    """List of tasks that this task depends on."""
    subtasks: List[str] = []
    """List of tasks that are completed only as part of this task."""
    status: TaskStatus = TaskStatus.OPEN
    """Current status of the task."""
    start_date: Optional[datetime] = None
    """Date when the task was started."""
    estimated_hours: Optional[int] = None
    """User estimated time required to complete the task."""
    calculated_hours: Optional[timedelta] = None
    """Calculated estimate of time required to complete the task."""
    actual_hours: Optional[timedelta] = None
    """Actual time taken to complete the task."""
    end_date: Optional[datetime] = None
    """Date when the task was completed."""
    users_assigned: List[Employee] = []
    """List of employees assigned to the task."""

    def __init__(self, **data):
        super().__init__(**data)
        if self.status is TaskStatus.COMPLETED:
            self.actual_hours = self.end_date - self.start_date
        if self.start_date is None:
            self.start_date = datetime.now()
        if self.calculated_hours is None:
            self.calculated_hours = calculate_time_estimate(self).calculated_hours
        if self.end_date is None:
            self.end_date = None


class Project(BaseModel):
    id: str
    name: str
    description: str
    tasks: List[Task] = []
    employees: List[str] = []  # Employee IDs