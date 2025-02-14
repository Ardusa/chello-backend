from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class CompanyBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company.
        founding_date (datetime): Date the company was founded.
        founding_member (UUID): Foreign key referencing the founding member of the company.
        task_limit (int): Maximum number of tasks allowed in the company.
        logo (str, optional): base64 image of the company logo.
    """

    id: UUID
    name: str
    founding_date: datetime
    founding_member: UUID
    task_limit: int
    logo: str = None


class CompanyCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the company.
        founding_member (str): Foreign key referencing the founding member of the company.
        task_limit (int): Maximum number of tasks allowed in the company.
        logo (str, optional): base64 image of the company logo.
    """

    name: str
    founding_member: str
    task_limit: int
    logo: str = None


class CompanyResponse(CompanyBase):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company.
        founding_date (str): Date the company was founded.
        founding_member (UUID): Foreign key referencing the founding member of the company.
    """

    class Config:
        from_attributes = True
