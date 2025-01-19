from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProjectBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the project, primary key.
        company_id (UUID): Foreign key referencing the company the project belongs to.
        name (str): Name of the project.
        description (str, optional): Description of the project.
        project_manager (UUID): Foreign key referencing the project creator/manager
    """
    id: UUID = None
    company_id: UUID
    name: str
    description: Optional[str]
    project_manager: UUID
    
class ProjectCreate(BaseModel):
    """
    Attributes:
        company_id (str): Foreign key referencing the company the project belongs to.
        name (str): Name of the project.
        description (str, optional): Description of the project.
        project_manager (str): Foreign key referencing the project creator/manager
    """
    company_id: str
    name: str
    description: Optional[str]
    project_manager: str

class ProjectResponse(ProjectBase):
    """
    Attributes:
        id (UUID): Unique identifier for the project, primary key.
        company_id (UUID): Foreign key referencing the company the project belongs to.
        name (str): Name of the project.
        description (str, optional): Description of the project.
        project_manager (UUID): Foreign key referencing the project creator/manager
    """
    class Config:
        from_attributes = True