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
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int): Maximum number of tasks the account can create.
        company_id (UUID, optional): Foreign key referencing the company the account belongs to.
        account_created (DateTime, optional): Date and time the account was created.
        last_login (DateTime): Date and time the account was last logged into.
        efficiency_score (float): Score indicating the efficiency of the account.
    """
    
    id: UUID
    name: str
    email: str
    password_hash: str
    company_id: Optional[UUID]
    manager_id: Optional[UUID]
    position: Optional[str]
    account_created: Optional[datetime]
    last_login: datetime    
    free_plan: bool
    task_limit: Optional[int]
    efficiency_score: float

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
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int): Maximum number of tasks the account can create.
        company_id (UUID, optional): Foreign key referencing the company the account belongs to.
        account_created (DateTime, optional): Date and time the account was created.
        last_login (DateTime): Date and time the account was last logged into.
        efficiency_score (float): Score indicating the efficiency of the account.
    """

    id: UUID
    name: str
    email: str
    manager_id: Optional[UUID]
    position: Optional[str]
    free_plan: bool
    task_limit: Optional[int]
    company_id: Optional[UUID]
    account_created: Optional[datetime]
    last_login: datetime
    efficiency_score: float

    class Config:
        from_attributes = True