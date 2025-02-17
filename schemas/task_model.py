from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class TaskBase(BaseModel):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        project_id (UUID): Foreign key referencing the project the task belongs to.
        assigned_to (UUID): Foreign key referencing the account the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
        order (int): Order of the task within the project.
        task_created (DateTime): Date and time the task was created.
        task_started (DateTime, optional): Date and time the task was started.
        task_completed (DateTime, optional): Date and time the task was completed.
        is_finished (bool): Boolean indicating if the task is finished.
        task_human_estimated_man_hours (float, optional): Estimated time of completion, given by the task creator.
        task_AI_estimated_man_hours (float, optional): Estimated time of completion, given by the neural network.
        task_actual_man_hours (float, optional): Actual time of completion.
    """
    id: UUID
    name: str
    description: Optional[str]
    project_id: UUID
    
    assigned_to: UUID
    parent_task_id: Optional[UUID]
    order: int
    
    task_created: datetime
    task_started: Optional[datetime]
    task_completed: Optional[datetime]
    is_finished: bool
    
    task_human_estimated_man_hours: Optional[float]
    task_AI_estimated_man_hours: Optional[float]
    task_actual_man_hours: Optional[float]
    
class TaskCreate(BaseModel):
    """
    Attributes:
        name (str): Name of the task.
        description (str): Description of the task.
        project_id (str): Foreign key referencing the project the task belongs to.
        assigned_to (str): Foreign key referencing the account the task is assigned to.
        parent_task_id (str, optional): Foreign key referencing the parent task of the task.
        order (int): Order of the task within the project.
    """
    name: str
    description: str
    project_id: str
    
    assigned_to: str
    parent_task_id: Optional[str]
    order: int
    

class TaskResponse(TaskBase):
    """
    Attributes:
        id (UUID): Unique identifier for the task, primary key.
        name (str): Name of the task.
        description (str, optional): Description of the task.
        project_id (UUID): Foreign key referencing the project the task belongs to.
        assigned_to (UUID): Foreign key referencing the account the task is assigned to.
        parent_task_id (UUID, optional): Foreign key referencing the parent task of the task.
        order (int): Order of the task within the project.
        task_created (DateTime): Date and time the task was created.
        task_started (DateTime, optional): Date and time the task was started.
        task_completed (DateTime, optional): Date and time the task was completed.
        is_finished (bool): Boolean indicating if the task is finished.
        task_human_estimated_man_hours (float, optional): Estimated time of completion, given by the task creator.
        task_AI_estimated_man_hours (float, optional): Estimated time of completion, given by the neural network.
        task_actual_man_hours (float, optional): Actual time of completion.
    """
    class Config:
        from_attributes = True
        
class TaskUpdate(BaseModel):
    """
    Attributes:
        id (str): Unique identifier for the task, primary key.
        name (str, optional): Name of the task.
        description (str, optional): Description of the task.
        project_id (str, optional): Foreign key referencing the project the task belongs to.
        assigned_to (str, optional): Foreign key referencing the account the task is assigned to.
        parent_task_id (str, optional): Foreign key referencing the parent task of the task.
        order (int, optional): Order of the task within the project.
        task_started (DateTime, optional): Date and time the task was started.
        task_completed (DateTime, optional): Date and time the task was completed.
        is_finished (bool, optional): Boolean indicating if the task is finished.
        task_human_estimated_man_hours (float, optional): Estimated time of completion, given by the task creator.
        task_AI_estimated_man_hours (float, optional): Estimated time of completion, given by the neural network.
    """
    id: str
    name: Optional[str]
    description: Optional[str]
    project_id: Optional[str]
    
    assigned_to: Optional[str]
    parent_task_id: Optional[str]
    order: Optional[int]
    
    task_started: Optional[datetime]
    task_completed: Optional[datetime]
    is_finished: Optional[bool]
    
    task_human_estimated_man_hours: Optional[float]
    task_AI_estimated_man_hours: Optional[float]