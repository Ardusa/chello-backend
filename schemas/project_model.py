from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProjectBase(BaseModel):
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
    """
    id: UUID
    name: str
    description: Optional[str]
    
    company_id: UUID
    project_manager: Optional[UUID]
    
    project_created: Optional[str]
    project_started: Optional[str]
    project_completed: Optional[str]
    is_finished: bool
    
class ProjectCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the project.
        description (str, optional): Description of the project.
        company_id (UUID): Foreign key referencing the company the project belongs to.
        project_manager (UUID, optional): Foreign key referencing the manager of the project
    """
    name: str
    description: Optional[str]
    company_id: str
    project_manager: Optional[str]

class ProjectResponse(ProjectBase):
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
    """
    class Config:
        from_attributes = True