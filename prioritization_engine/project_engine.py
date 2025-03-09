import uuid
import models
from services import get_db, load_project
from fastapi import Depends
from sqlalchemy.orm import Session
from .task_engine import calculate_task_efficiency, refresh_task_man_hours

def refresh_project_man_hours(project_id: uuid.UUID, db: Session = Depends(get_db)) -> models.Project:
    """
    Given a project ID, refresh the project's human estimated man hours, AI estimated man hours, and actual man hours.
    Will not update the project in the database.
    """
    project = load_project(project_id=project_id, db=db)
    
    project.project_human_estimated_man_hours = 0
    project.project_AI_estimated_man_hours = 0
    project.project_actual_man_hours = 0

    for task in project.tasks:
        task = refresh_task_man_hours(task_id=task.id, db=db)
        project.project_human_estimated_man_hours += task.task_human_estimated_man_hours
        project.project_AI_estimated_man_hours += task.task_AI_estimated_man_hours
        project.project_actual_man_hours += task.task_actual_man_hours

    return project

def calculate_project_efficiency(project_id: uuid.UUID, db: Session = Depends(get_db)) -> float:
    """
    Calculate the efficiency of a project based on a weighted average of the efficiency of each task.
    """
    project = refresh_project_man_hours(project_id=project_id, db=db)
    
    total_efficiency = 0.0
    total_weight = 0.0

    for task in project.tasks:
        task_efficiency = calculate_task_efficiency(task, db)
        weight = task.task_AI_estimated_man_hours
        total_efficiency += task_efficiency * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return total_efficiency / total_weight