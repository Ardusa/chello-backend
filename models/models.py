from sqlalchemy import (
    Column,
    Double,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

task_account_association = Table(
    "task_account_association",
    Base.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id")),
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id")),
)
"""
This table is used to create a many-to-many relationship between Task and Account.
"""


class Account(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the Account, primary key.
        name (str): Name of the Account.
        email (str, unique): Unique email address of the Account.
        password_hash (str): Hashed password of the Account.

        company_id (UUID): Foreign key referencing the company the Account belongs to. Given to all to allow smooth transition from individual to company accounts.
        manager_id (UUID, optional): Foreign key referencing the manager of the Account, nullable.
        position (str, optional): Position of the Account within the company.

        account_created (DateTime): Date and time the Account was created.
        last_login (DateTime): Date and time the Account last logged in.

        free_plan (bool): Boolean indicating if the Account is on a free plan.
        task_limit (int, optional): Maximum number of tasks the Account can create.

        efficiency_score (float): Efficiency score of this user.
        tasks (List(Task)): List of tasks assigned to this Account.
    """

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
        default=uuid.uuid4,
    )
    manager_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    position = Column(String, nullable=True)

    account_created = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    last_login = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    free_plan = Column(Boolean, default=True, nullable=False)
    task_limit = Column(Integer, default=0, nullable=True)

    efficiency_score = Column(Double, default=1.0, nullable=False)
    tasks = relationship(
        "Task", secondary="task_account_association", back_populates="accounts"
    )


class Task(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        project_id (UUID): Foreign key referencing the project the task belongs to.

        assigned_to (UUID): Foreign key referencing the account the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
        task_order (int): Order of the task within the project.

        task_created (DateTime): Date and time the task was created.
        task_started (DateTime, optional): Date and time the task was started.
        task_completed (DateTime, optional): Date and time the task was completed.
        is_finished (bool): Boolean indicating if the task is finished.

        task_human_estimated_man_hours (float, optional): Estimated time of completion, given by the task creator.
        task_AI_estimated_man_hours (float, optional): Estimated time of completion, given by the neural network.
        task_actual_man_hours (float, optional): Actual time of completion.
    """

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    assigned_to = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    order = Column(Integer, default=0, nullable=False)

    accounts = relationship(
        "Account", secondary="task_account_association", back_populates="tasks"
    )

    task_created = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    task_started = Column(DateTime, nullable=True)
    task_completed = Column(DateTime, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)

    task_human_estimated_man_hours = Column(Double, nullable=True)
    task_AI_estimated_man_hours = Column(Double, nullable=True)
    task_actual_man_hours = Column(Double, nullable=True)


class Project(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the project, primary key.
        name (str): Name of the project.
        description (str, optional): Description of the project.

        company_id (UUID): Foreign key referencing the company the project belongs to.
        project_manager (UUID, optional): Foreign key referencing the manager of the project.

        project_created (DateTime): Date and time the project was created.
        project_started (DateTime, optional): Date and time the project was started.
        project_completed (DateTime, optional): Date and time the project was completed.
        is_finished (bool): Boolean indicating if the project is finished.

        tasks (List(Task)): List of tasks in the project.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    project_manager = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )
    
    project_created = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    project_started = Column(DateTime, nullable=True)
    project_completed = Column(DateTime, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)
    
    tasks = relationship("Task", backref="project")


class Company(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company.
        founding_date (DateTime): Date the company was founded.
        founding_member (UUID): Foreign key referencing the founding member of the company.

        accounts (List(Account)): List of accounts in the company.
        projects (List(Project)): List of projects in the company.
        task_limit (int, optional): Maximum number of tasks the company can create.
    """
    
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    founding_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    founding_member = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    accounts = relationship("Account", backref="company")
    projects = relationship("Project", backref="company")
    
    task_limit = Column(Integer, default=0, nullable=True)