from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class TaskBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        project_id (UUID): Foreign key referencing the project the task belongs to.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        assigned_to (UUID, optional): Foreign key referencing the employee the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
    """
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str]
    assigned_to: Optional[UUID]
    parent_task_id: Optional[UUID]
    
class TaskCreate(TaskBase):
    """
    Attributes:
        project_id (UUID): Foreign key referencing the project the task belongs to.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        assigned_to (UUID, optional): Foreign key referencing the employee the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
    """
    pass

class TaskResponse(TaskBase):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        project_id (UUID): Foreign key referencing the project the task belongs to.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        assigned_to (UUID, optional): Foreign key referencing the employee the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
    """
    class Config:
        from_attributes = True