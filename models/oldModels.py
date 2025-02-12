from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for many-to-many relationship between Task and Account
task_account_association = Table(
    "task_account_association",
    Base.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id")),
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id")),
)
"""
This table is used to create a many-to-many relationship between Task and Account.
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
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )


class Account(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the Account, primary key.
        company_id (UUID): Foreign key referencing the company the Account belongs to.
        name (str): Name of the Account.
        position (int): Position of the Account within the company.
        email (str, unique): Unique email address of the Account.
        manager (UUID, optional): Foreign key referencing the manager of the Account, nullable.
        password_hash (str): Hashed password of the Account.
    """

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    position = Column(String, nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)


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
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )


class Task(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        project_id (UUID): Foreign key referencing the project the task belongs to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
        start_time (DateTime, optional): Start time of the task.
        end_time (DateTime, optional): End time of the task.
        completed (bool): Status of the task.
        order (int): Order of the task within the project.

    Relationships:
        project (Project): Relationship to the project the task belongs to.
        parent_task (Task, optional): Relationship to the parent task of the task.
        subtasks (List[Task]): Relationship to the subtasks of the task.
        Accounts (List[Account]): Relationship to the Accounts assigned to the task.
    """

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    order = Column(Integer, nullable=False, default=0)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)

    # Relationships
    project = relationship("Project", backref="tasks")
    parent_task = relationship(
        "Task",
        remote_side=[id],
        backref=backref("subtasks", cascade="all, delete-orphan"),
    )
    
    # Not using at all
    Accounts = relationship(
        "Account", secondary=task_account_association, backref="tasks"
    )

    def complete(self):
        self.completed = True
        self.end_time = datetime.now(timezone.utc)
