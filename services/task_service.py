from collections import OrderedDict
from models import Task, Project, task_employee_association
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import Optional
from services import get_db


def create_task(
    task: Task,
    project_id: int,
    parent_task_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    db_task = Task(**task.dict(), project_id=project_id, parent_task_id=parent_task_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def load_task(task_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.id == task_id).first()


def load_project_tasks(
    employee_id=None, project_id=None, db: Session = Depends(get_db)
):
    """
    Get all tasks relevant to a specific employee for a specific project.

    Parameters:
    employee_id (UUID, optional): The ID of the employee. If provided, the function will filter tasks to only include those assigned to this employee.
    project_id (UUID, optional): The ID of the project. If provided, the function will filter tasks to only include those within this project.

    Returns:
    dict:
        - If both employee_id and project_id are provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
        - If only project_id is provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
        - If only employee_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.
        - If neither employee_id nor project_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.

    The function recursively builds the dictionary to include all subtasks and their subtasks, and so on. If employee_id is provided, only subtasks assigned to the employee are included.
    """

    query = db.query(Task)

    def build_task_dict(task):
        """Recursively build an ordered dictionary of tasks to their subtasks."""
        task_dict = OrderedDict({task: []})
        for subtask in sorted(task.subtasks, key=lambda t: t.order):
            if not employee_id or employee_id in [emp.id for emp in subtask.employees]:
                task_dict[task].append(build_task_dict(subtask))
        return task_dict

    if employee_id:
        # Check if the employee is the project manager of any projects
        managed_projects = (
            db.query(Project).filter(Project.project_manager == employee_id).all()
        )
        if managed_projects:
            if project_id:
                # If project_id is provided, check if the employee is the project manager of the project
                project = db.query(Project).filter(Project.id == project_id).first()
                if project and project.project_manager == employee_id:
                    query = query.filter(Task.project_id == project_id)
                else:
                    # ! Incorrect Usage
                    raise HTTPException(
                        status_code=403, detail="Not authorized to access this project"
                    )
            else:
                # Return all projects managed by the employee
                projects = OrderedDict()
                for project in managed_projects:
                    project_tasks = (
                        db.query(Task)
                        .filter(Task.project_id == project.id)
                        .order_by(Task.order)
                        .all()
                    )
                    project_dict = OrderedDict()
                    for task in project_tasks:
                        project_dict.update(build_task_dict(task))
                    projects[project.id] = project_dict
                return projects
        else:
            query = query.join(task_employee_association).filter(
                task_employee_association.c.employee_id == employee_id
            )

    if project_id:
        query = query.filter(Task.project_id == project_id)

    # Order tasks by the order column
    # query = query.order_by(Task.order)

    tasks = query.all()

    if employee_id and not project_id:
        # Separate tasks into each project the employee is part of
        projects = OrderedDict()
        for task in tasks:
            if task.project_id not in projects:
                projects[task.project_id] = OrderedDict()
            projects[task.project_id].update(build_task_dict(task))
        return projects

    if not employee_id and not project_id:
        # Separate tasks into each project
        projects = OrderedDict()
        for task in tasks:
            if task.project_id not in projects:
                projects[task.project_id] = OrderedDict()
            projects[task.project_id].update(build_task_dict(task))
        return projects

    # Build the ordered dictionary for tasks and their subtasks
    task_dict = OrderedDict()
    for task in tasks:
        task_dict.update(build_task_dict(task))

    return task_dict