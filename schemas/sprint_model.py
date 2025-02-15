from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SprintBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the sprint, primary key.
        name (str): Name of the sprint.
        description (str, optional): Description of the sprint.
        project_id (UUID): Foreign key referencing the project the sprint belongs to.
        sprint_manager_id (UUID): Foreign key referencing the account the sprint is assigned to.
        sprint_created (DateTime): Date and time the sprint was created.
        sprint_started (DateTime, optional): Date and time the sprint was started.
        sprint_completed (DateTime, optional): Date and time the sprint was completed.
        is_finished (bool): Boolean indicating if the sprint is finished.
        progress (float): Progress of the sprint as a percentage.
    """
    id: UUID
    name: str
    description: Optional[str]
    project_id: UUID
    sprint_manager_id: UUID
    sprint_created: datetime
    sprint_started: Optional[datetime]
    sprint_completed: Optional[datetime]
    is_finished: bool
    progress: float

class SprintCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the sprint.
        description (str, optional): Description of the sprint.
        project_id (str): Foreign key referencing the project the sprint belongs to.
        sprint_manager_id (str): Foreign key referencing the account the sprint is assigned to.
    """
    name: str
    description: Optional[str]
    project_id: str
    sprint_manager_id: str

class SprintResponse(SprintBase):
    """
    Attributes:
        id (UUID): Unique identifier for the sprint, primary key.
        name (str): Name of the sprint.
        description (str, optional): Description of the sprint.
        project_id (UUID): Foreign key referencing the project the sprint belongs to.
        sprint_manager_id (UUID): Foreign key referencing the account the sprint is assigned to.
        sprint_created (DateTime): Date and time the sprint was created.
        sprint_started (DateTime, optional): Date and time the sprint was started.
        sprint_completed (DateTime, optional): Date and time the sprint was completed.
        is_finished (bool): Boolean indicating if the sprint is finished.
        progress (float): Progress of the sprint as a percentage.
    """
    class Config:
        from_attributes = True