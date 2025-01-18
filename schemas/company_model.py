from pydantic import BaseModel
from uuid import UUID


class CompanyBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company.
        founding_member (UUID): Foreign key referencing the founding member of the company.
    """

    id: UUID
    name: str
    founding_member: UUID


class CompanyCreate(CompanyBase):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company.
        founding_member (UUID): Foreign key referencing the founding member of the company.
    """

    pass


class CompanyResponse(CompanyBase):
    """
    Attributes:
        id (UUID): Unique identifier for the company, primary key.
        name (str): Name of the company.
        founding_member (UUID): Foreign key referencing the founding member of the company
    """

    class Config:
        from_attributes = True
