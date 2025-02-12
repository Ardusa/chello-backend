from pydantic import BaseModel
from typing import List, Optional
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
    
class TaskCreate(BaseModel):
    """
    Attributes:
        project_id (str): Foreign key referencing the project the task belongs to.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        assigned_to (str, optional): Foreign key referencing the employee the task is assigned to.
        parent_task_id (str, optional): Foreign key referencing the parent task of the task.
    """
    project_id: str
    name: str
    description: str
    assigned_to: Optional[str]
    parent_task_id: Optional[str]

class TaskCreateRecursive(TaskCreate):
    """
    Attributes:
        project_id (UUID): Foreign key referencing the project the task belongs to.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        assigned_to (UUID, optional): Foreign key referencing the employee the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
        subtasks (List[TaskCreateRecursive], optional): List of subtasks of the task.
    """
    subtasks: Optional[List[TaskCreate]]
    

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