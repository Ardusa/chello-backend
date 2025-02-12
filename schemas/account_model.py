from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AccountBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the account, primary key.
        name (str): Name of the account.
        email (str, unique): Unique email address of the account.
        password (str): Password of the account.
        manager_id (UUID, optional): Foreign key referencing the manager of the account, nullable.
        position (int): Position of the account within the company.
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
    password: str
    company_id: str
    manager_id: Optional[str]
    position: Optional[str]
    account_created: Optional[str]
    last_login: str    
    free_plan: bool
    task_limit: Optional[int]
    efficiency_score: float

class AccountCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the account.
        email (str): Email address of the account.
        password (str): Password of the account.
        manager_id (UUID, optional): Foreign key referencing the manager of the account, nullable.
        position (str): Position of the account within the company.
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int, optional): Maximum number of tasks the account can create.
        company_id (UUID, optional): Foreign key referencing the company the account
    """
    
    name: str
    email: str
    password: str
    manager_id: Optional[str]
    position: str
    free_plan: bool
    task_limit: Optional[int]
    company_id: Optional[str]

class AccountResponse(AccountBase):
    """
    Attributes:
        id (UUID): Unique identifier for the account, primary key.
        name (str): Name of the account.
        email (str, unique): Unique email address of the account.
        password (str): Password of the account.
        manager_id (UUID, optional): Foreign key referencing the manager of the account, nullable.
        position (int): Position of the account within the company.
        free_plan (bool): Boolean indicating if the account is on a free plan.
        task_limit (int): Maximum number of tasks the account can create.
        company_id (UUID, optional): Foreign key referencing the company the account belongs to.
        account_created (DateTime, optional): Date and time the account was created.
        last_login (DateTime): Date and time the account was last logged into.
        efficiency_score (float): Score indicating the efficiency of the account.
    """

    class Config:
        from_attributes = True