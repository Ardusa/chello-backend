from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Association table for many-to-many relationship between Task and Employee
task_employee_association = Table(
    "task_employee_association",
    Base.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id")),
    Column("employee_id", UUID(as_uuid=True), ForeignKey("employees.id")),
)
"""
This table is used to create a many-to-many relationship between Task and Employee.
"""


class Company(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company, unique.
        founding_member (UUID): Foreign key referencing the founding member of the company.
    """

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    founding_member = Column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )


class Employee(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the employee, primary key.
        company_id (UUID): Foreign key referencing the company the employee belongs to.
        name (str): Name of the employee.
        position (int): Position of the employee within the company.
        email (str, unique): Unique email address of the employee.
        manager (UUID, optional): Foreign key referencing the manager of the employee, nullable.
        password_hash (str): Hashed password of the employee.
    """

    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    position = Column(Integer, nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)


class Project(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the project, primary key.
        company_id (UUID): Foreign key referencing the company the project belongs to.
        name (str): Name of the project.
        description (str, optional): Description of the project.
        project_manager (UUID): Foreign key referencing the project creator/manager.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    project_manager = Column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )


class Task(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        project_id (UUID): Foreign key referencing the project the task belongs to.
        start_time (DateTime, optional): Start time of the task.
        end_time (DateTime, optional): End time of the task.
        completed (bool): Status of the task.
        order (int): Order of the task within the project.

    Relationships:
        project (Project): Relationship to the project the task belongs to.
        parent_task (Task, optional): Relationship to the parent task of the task.
        subtasks (List[Task]): Relationship to the subtasks of the task.
        employees (List[Employee]): Relationship to the employees assigned to the task.
    """

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    project = relationship("Project", backref="tasks")
    parent_task = relationship(
        "Task",
        remote_side=[id],
        backref=backref("subtasks", cascade="all, delete-orphan"),
    )
    employees = relationship(
        "Employee", secondary=task_employee_association, backref="tasks"
    )

    def complete(self):
        self.completed = True
        self.end_time = datetime.now(timezone.utc)
