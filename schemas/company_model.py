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
    """

    id: UUID
    name: str
    founding_date: datetime
    founding_member: UUID


class CompanyCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the company.
        founding_member (UUID): Foreign key referencing the founding member of the company.
    """

    name: str
    founding_member: str


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
