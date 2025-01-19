from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class EmployeeBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the employee, primary key.
        company_id (UUID): Foreign key referencing the company the employee belongs to.
        name (str): Name of the employee.
        position (int): Position of the employee within the company.
        email (str, unique): Unique email address of the employee.
        manager (UUID, optional): Foreign key referencing the manager of the employee, nullable.
    """
    
    id: UUID
    name: str
    email: str
    company_id: UUID
    position: str
    manager_id: Optional[UUID]

class EmployeeCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the employee.
        email (str, unique): Unique email address of the employee.
        password (str): Password of the employee.
        company_id (UUID): Foreign key referencing the company the employee belongs to.
        position (int): Position of the employee within the company.
        manager_id (UUID, optional): Foreign key referencing the manager of the employee, nullable.
    """
    
    name: str
    email: str
    password: str
    company_id: str
    position: str
    manager_id: Optional[str]

class EmployeeResponse(EmployeeBase):
    """
    Attributes:
        id (UUID): Unique identifier for the employee, primary key.
        company_id (UUID): Foreign key referencing the company the employee belongs to.
        name (str): Name of the employee.
        position (int): Position of the employee within the company.
        email (str, unique): Unique email address of the employee.
        manager (UUID, optional): Foreign key referencing the manager of the employee, nullable.
    """
    class Config:
        from_attributes = True