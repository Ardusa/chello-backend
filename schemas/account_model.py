from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class AccountBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the account, primary key.
        name (str): Name of the account.
        email (str, unique): Unique email address of the account.
        password_hash (str): Password of the account.
        manager_id (UUID, optional): Foreign key referencing the manager of the account, nullable.
        position (str): Job position of the user.
        manager (bool): Boolean indicating if the account is a manager.
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int): Maximum number of tasks the account can create.
        company_id (UUID, optional): Foreign key referencing the company the account belongs to.
        account_created (DateTime, optional): Date and time the account was created.
        last_login (DateTime): Date and time the account was last logged into.
        efficiency_score (float): Score indicating the efficiency of the account.
        work_hours (list): List of work hours for each day of the week.
    """

    id: UUID
    name: str
    email: str
    password_hash: str
    company_id: Optional[UUID]
    manager_id: Optional[UUID]
    position: Optional[str]
    manager: bool
    account_created: Optional[datetime]
    last_login: datetime
    free_plan: bool
    task_limit: Optional[int]
    efficiency_score: float
    work_hours: list = [
        {"day": "Monday", "start": "", "end": ""},
        {"day": "Tuesday", "start": "", "end": ""},
        {"day": "Wednesday", "start": "", "end": ""},
        {"day": "Thursday", "start": "", "end": ""},
        {"day": "Friday", "start": "", "end": ""},
        {"day": "Saturday", "start": "", "end": ""},
        {"day": "Sunday", "start": "", "end": ""},
    ]


class AccountCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the account.
        email (str): Email address of the account.
        password (str): Password of the account.
        manager_id (str, optional): Foreign key referencing the manager of the account, nullable.
        position (str): Job position of the user.
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int, optional): Maximum number of tasks the account can create.
        company_id (str, optional): Foreign key referencing the company the account belongs to.
        create_company (bool): Boolean indicating if a new company should be created.
    """

    name: str
    email: str
    password: str
    manager_id: Optional[str]
    position: Optional[str]
    free_plan: bool
    task_limit: Optional[int]
    company_id: Optional[str]
    create_company: bool = False


class AccountResponse(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the account, primary key.
        name (str): Name of the account.
        email (str, unique): Unique email address of the account.
        manager_id (UUID, optional): Foreign key referencing the manager of the account, nullable.
        position (str): Job position of the user.
        manager (bool): Boolean indicating if the account is a manager.
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int): Maximum number of tasks the account can create.
        company_id (UUID, optional): Foreign key referencing the company the account belongs to.
        account_created (DateTime, optional): Date and time the account was created.
        last_login (DateTime): Date and time the account was last logged into.
        efficiency_score (float): Score indicating the efficiency of the account.
        work_hours (list): List of work hours for each day of the week.
    """

    id: UUID
    name: str
    email: str

    manager_id: Optional[UUID]
    position: Optional[str]
    company_id: Optional[UUID]
    manager: bool

    free_plan: bool
    task_limit: Optional[int]

    account_created: Optional[datetime]
    last_login: datetime

    efficiency_score: float
    work_hours: list = [
        {"day": "Monday", "start": "", "end": ""},
        {"day": "Tuesday", "start": "", "end": ""},
        {"day": "Wednesday", "start": "", "end": ""},
        {"day": "Thursday", "start": "", "end": ""},
        {"day": "Friday", "start": "", "end": ""},
        {"day": "Saturday", "start": "", "end": ""},
        {"day": "Sunday", "start": "", "end": ""},
    ]

    class Config:
        from_attributes = True


class AccountUpdate(BaseModel):
    """
    Attributes:
        id (str, optional): Unique identifier for the account, primary key.
        name (str, optional): Name of the account.
        email (str, optional): Email address of the account.

        manager_id (str, optional): Foreign key referencing the manager of the account, nullable.
        position (str, optional): Job position of the user.
        company_id (str, optional): Foreign key referencing the company the account belongs to.
        manager (bool, optional): Boolean indicating if the account is a manager.

        free_plan (bool, optional): Boolean indicating if the account is on a free plan.
        task_limit (int, optional): Maximum number of tasks the account can create.

        account_created (DateTime, optional): Date and time the account was created.
        last_login (DateTime, optional): Date and time the account was last logged into.

        efficiency_score (float, optional): Score indicating the efficiency of the account.
        work_hours (list, optional): List of work hours for each day of the week.
    """

    id: Optional[str]
    name: Optional[str]
    email: Optional[str]

    manager_id: Optional[str]
    position: Optional[str]
    company_id: Optional[str]
    manager: Optional[bool]

    free_plan: Optional[bool]
    task_limit: Optional[int]

    account_created: Optional[datetime]
    last_login: Optional[datetime]

    efficiency_score: Optional[float]
    work_hours: Optional[list]
