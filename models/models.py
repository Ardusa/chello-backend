import json
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

        company_id (UUID, optional): Foreign key referencing the company the Account belongs to.
        manager_id (UUID, optional): Foreign key referencing the manager of the Account, nullable.
        position (str, optional): Position of the Account within the company.
        manager (bool): Boolean indicating if the Account is a manager.

        account_created (DateTime): Date and time the Account was created.
        last_login (DateTime): Date and time the Account last logged in.

        free_plan (bool): Boolean indicating if the Account is on a free plan.
        task_limit (int, optional): Maximum number of tasks the Account can create.

        efficiency_score (float): Efficiency score of this user.
        tasks (List(Task)): List of tasks assigned to this Account.
        sprints (List[Sprint]): List of sprints assigned to this Account.
        work_hours (List[Dict[str, str]]): List of work hours for each day of the week.
    """

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=True,
        # default=uuid.uuid4,
    )
    manager_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    position = Column(String, nullable=True)

    @property
    def manager(self):
        if self.company is None:
            return False
        return any(account.manager_id == self.id for account in self.company.accounts)

    account_created = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    last_login = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    free_plan = Column(Boolean, default=True, nullable=False)
    task_limit = Column(Integer, nullable=True)

    efficiency_score = Column(Double, default=1.0, nullable=False)
    tasks = relationship(
        "Task", secondary="task_account_association", back_populates="accounts"
    )

    sprints = relationship(
        "Sprint", backref="account", foreign_keys="[Sprint.account_id]"
    )

    work_hours_str = Column(
        String,
        nullable=True,
        default=lambda: json.dumps(
            [
                {"day": "Monday", "start": "09:00", "end": "17:00"},
                {"day": "Tuesday", "start": "09:00", "end": "17:00"},
                {"day": "Wednesday", "start": "09:00", "end": "17:00"},
                {"day": "Thursday", "start": "09:00", "end": "17:00"},
                {"day": "Friday", "start": "09:00", "end": "17:00"},
                {"day": "Saturday", "start": "", "end": ""},
                {"day": "Sunday", "start": "", "end": ""},
            ]
        ),
    )

    @property
    def work_hours(self) -> list[dict]:
        return json.loads(self.work_hours_str)

    @work_hours.setter
    def work_hours(self, value: list[dict]):
        self.work_hours_str = json.dumps(value)


class Task(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        project_id (UUID): Foreign key referencing the project the task belongs to.

        assigned_to (UUID): Foreign key referencing the account the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
        order (int): Order of the task within the project.

        accounts (List(Account)): List of accounts assigned to the task.
        subtasks (List(Task)): List of subtasks of the task.

        task_created (DateTime): Date and time the task was created.
        task_started (DateTime, optional): Date and time the task was started.
        task_completed (DateTime, optional): Date and time the task was completed.
        is_finished (bool): Boolean indicating if the task is finished.
        progress (float): Progress of the task.

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
    subtasks = relationship("Task", backref="parent_task", remote_side=[id])

    task_created = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    task_started = Column(DateTime, nullable=True)
    task_completed = Column(DateTime, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)
    progress = Column(Double, default=0, nullable=False)

    task_human_estimated_man_hours = Column(Double, nullable=True)
    task_AI_estimated_man_hours = Column(Double, nullable=True)
    task_actual_man_hours = Column(Double, nullable=True)


class Project(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the project, primary key.
        name (str): Name of the project.
        description (str, optional): Description of the project.

        company_id (UUID, optional): Foreign key referencing the company the project belongs to.
        project_manager (UUID): Foreign key referencing the manager of the project.

        project_created (DateTime): Date and time the project was created.
        project_started (DateTime, optional): Date and time the project was started.
        project_completed (DateTime, optional): Date and time the project was completed.
        is_finished (bool): Boolean indicating if the project is finished.

        tasks (List(Task)): List of tasks in the project.

        project_human_estimated_man_hours (float, optional): Estimated time of completion, given by the project creator.
        project_AI_estimated_man_hours (float, optional): Estimated time of completion, given by the neural network.
        project_actual_man_hours (float, optional): Actual time of completion.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    project_manager = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )

    project_created = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    project_started = Column(DateTime, nullable=True)
    project_completed = Column(DateTime, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)

    tasks = relationship("Task", backref="project", foreign_keys="[Task.project_id]")

    project_human_estimated_man_hours = Column(Double, nullable=True)
    project_AI_estimated_man_hours = Column(Double, nullable=True)
    project_actual_man_hours = Column(Double, nullable=True)


class Sprint(Base):
    """
    Attributes:
        id (UUID): Unique identifier for the sprint, primary key.
        name (str): Name of the sprint.
        description (str, optional): Description of the sprint.

        sprint_manager_id (UUID): Foreign key referencing the account the sprint belongs to.
        project_id (UUID): Foreign key referencing the project the sprint belongs to.

        sprint_created (DateTime): Date and time the sprint was created.
        sprint_started (DateTime, optional): Date and time the sprint was started.
        sprint_duration (float, optional): Duration of the sprint in hours.
        sprint_completed (DateTime, optional): Date and time the sprint was completed.
        is_finished (bool): Boolean indicating if the sprint is finished.

        tasks (List(Task)): List of tasks in the sprint.
        accounts (List(Account)): List of accounts in the sprint.
    """

    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    sprint_manager_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    sprint_created = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    sprint_started = Column(DateTime, nullable=True)
    sprint_duration = Column(Double, nullable=True)
    sprint_completed = Column(DateTime, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)

    tasks = relationship("Task", backref="sprint", foreign_keys="[Task.sprint_id]")
    accounts = relationship(
        "Account", backref="sprints", foreign_keys="[Sprint.account_id]"
    )


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

        logo (str, optional): base64 image of the company logo.
    """

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    founding_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    founding_member = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )

    accounts = relationship(
        "Account", backref="company", foreign_keys="[Account.company_id]"
    )
    projects = relationship(
        "Project", backref="company", foreign_keys="[Project.company_id]"
    )

    task_limit = Column(Integer, default=0, nullable=False)

    logo = Column(String, nullable=True)
