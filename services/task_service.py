from collections import OrderedDict
import uuid
from models import Task, Project, task_employee_association
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Optional
from models.models import Employee
from schemas import task_model
from services import get_db


def create_task(
    task: task_model.TaskCreate,
    project_id: uuid.UUID,
    parent_task_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    db_task = Task(
        project_id=project_id,
        name=task.name,
        description=task.description,
        parent_task_id=uuid.UUID(parent_task_id) if parent_task_id else None,
        assigned_to=uuid.UUID(task.assigned_to) if task.assigned_to else None,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def load_task(task_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.id == task_id).first()


def load_project_tasks(
    employee_id=None,
    project_id=None,
    db: Session = Depends(get_db),
):
    """
    Get all tasks relevant to a specific employee for a specific project.

    Parameters:
    employee_id (UUID, optional): The ID of the employee. If provided, the function will filter tasks to only include those assigned to this employee.
    project_id (UUID, optional): The ID of the project. If provided, the function will filter tasks to only include those within this project.

    Returns:
    dict:
        - If both employee_id and project_id are provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
        - If only employee_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.
        - If only project_id is provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
        - If neither employee_id nor project_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.

    The function recursively builds the dictionary to include all subtasks and their subtasks, and so on. If employee_id is provided, only subtasks assigned to the employee are included.
    """

    query = db.query(Task)

    if employee_id and project_id:
        # If the project specified happens to be managed by the eployee, return all tasks in the project
        if (
            project_id
            in db.query(Project.id).filter(Project.project_manager == employee_id).all()
        ):
            query = query.filter(Task.project_id == project_id)

        # If the employee is not a project manager, check if the employee is assigned to any tasks
        else:
            query = (
                db.query(Task)
                .filter(Task.project_id == project_id)
                .filter(Task.assigned_to == employee_id)
                .order_by(Task.order)
                .group_by(Task.project_id)
            )

    elif employee_id and not project_id:
        query = (
            query.filter(Task.assigned_to == employee_id)
            .order_by(Task.order)
            .group_by(Task.project_id)
        )

    elif not employee_id and project_id:
        query = query.filter(Task.project_id == project_id).order_by(Task.order)

    else:
        query = query.order_by(Task.order).group_by(Task.project_id)
    
    
    # Code for creating the dictionary
    def build_task_dict(project: OrderedDict[uuid.UUID, OrderedDict[uuid.UUID, any]], task: Task):
        """Recursively build an ordered dictionary of tasks to their subtasks."""
        
        def sort_recursive_dict(d: OrderedDict):
            """Recursively sort an OrderedDict by the 'order' attribute of the keys."""
            sorted_dict = OrderedDict()
            for key, value in sorted(d.items(), key=lambda item: item[0].order):
                if isinstance(value, OrderedDict):
                    sorted_dict[key] = sort_recursive_dict(value)
                else:
                    sorted_dict[key] = value
            return sorted_dict
    
        if not task.parent_task_id:
            project[task] = []
            project = OrderedDict(
                sorted(project.items(), key=lambda item: item[0].order)
            )
        
        else:
            def recursive_insert(project, task):
                for id, value in project.items():
                    if task.parent_task_id == id:
                        value.append(task)
                        value.sort(key=lambda t: t.order)
                        return True
                    if isinstance(value, OrderedDict):
                        if recursive_insert(value, task):
                            return True
                return False

            if not recursive_insert(project, task):
                raise ValueError("Task Parent Not Present")

        sort_recursive_dict(project)
        return project

    tasks = query.all()

    if employee_id and project_id:
        # Order the project based on the employees role in the project.
        project = OrderedDict()
        for task in tasks:
            project.update(build_task_dict(project, task))

    elif employee_id and not project_id:
        # Separate tasks into each project the employee is part of
        projects = OrderedDict()
        for task in tasks:
            if task.project_id not in projects:
                projects[task.project_id] = OrderedDict()
            projects[task.project_id].update(build_task_dict(projects[task.project_id], task))
        return projects

    elif not employee_id and project_id:
        # Sort all the tasks for one whole project
        project = OrderedDict()
        for task in tasks:
            project.update(build_task_dict(project, task))
        return project

    else:
        # Separate tasks into each project
        projects = OrderedDict()
        for task in tasks:
            if task.project_id not in projects:
                projects[task.project_id] = OrderedDict()
            projects[task.project_id].update(build_task_dict(projects, task))
        return projects


# def load_project_tasks(
#     employee_id=None,
#     project_id=None,
#     db: Session = Depends(get_db),
# ):
#     """
#     Get all tasks relevant to a specific employee for a specific project.

#     Parameters:
#     employee_id (UUID, optional): The ID of the employee. If provided, the function will filter tasks to only include those assigned to this employee.
#     project_id (UUID, optional): The ID of the project. If provided, the function will filter tasks to only include those within this project.

#     Returns:
#     dict:
#         - If both employee_id and project_id are provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
#         - If only employee_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.
#         - If only project_id is provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
#         - If neither employee_id nor project_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.

#     The function recursively builds the dictionary to include all subtasks and their subtasks, and so on. If employee_id is provided, only subtasks assigned to the employee are included.
#     """

#     query = db.query(Task)

#     def build_task_dict(task):
#         """Recursively build an ordered dictionary of tasks to their subtasks."""
#         task_dict = OrderedDict({task: []})
#         for subtask in sorted(task.subtasks, key=lambda t: t.order):
#             if not employee_id or employee_id == subtask.assigned_to:
#                 task_dict[task].append(build_task_dict(subtask))
#         return task_dict

#     if employee_id and project_id:
#         # Check if the employee is the project manager of the specified project
#         is_project_manager = db.query(Project).filter(
#             Project.id == project_id,
#             Project.project_manager == employee_id
#         ).first()

#         if is_project_manager:
#             query = query.filter(Task.project_id == project_id)
#         else:
#             # If the employee is not a project manager, check if the employee is assigned to any tasks
#             query = (
#                 db.query(Task)
#                 .join(task_employee_association, Task.id == task_employee_association.c.task_id)
#                 .filter(
#                     task_employee_association.c.employee_id == employee_id,
#                     Task.project_id == project_id,
#                 )
#             )

#     elif employee_id and not project_id:
#         query = query.join(task_employee_association).filter(
#             task_employee_association.c.employee_id == employee_id
#         )

#     if project_id:
#         query = query.filter(Task.project_id == project_id)

#     tasks = query.all()

#     if employee_id and not project_id:
#         # Separate tasks into each project the employee is part of
#         projects = OrderedDict()
#         for task in tasks:
#             if task.project_id not in projects:
#                 projects[task.project_id] = OrderedDict()
#             projects[task.project_id].update(build_task_dict(task))
#         return projects

#     if not employee_id and not project_id:
#         # Separate tasks into each project
#         projects = OrderedDict()
#         for task in tasks:
#             if task.project_id not in projects:
#                 projects[task.project_id] = OrderedDict()
#             projects[task.project_id].update(build_task_dict(task))
#         return projects

#     # Build the ordered dictionary for tasks and their subtasks
#     task_dict = OrderedDict()
#     for task in tasks:
#         task_dict.update(build_task_dict(task))

#     return task_dict


def create_task_recursive(
    task_data: task_model.TaskCreateRecursive,
    project_id: str,
    db: Session,
    parent_task_id: Optional[str] = None,
):
    # Create the main task
    task = Task(
        project_id=project_id,
        name=task_data.name,
        description=task_data.description,
        parent_task_id=parent_task_id,
        assigned_to=task_data.assigned_to,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Recursively create subtasks
    for subtask_data in task_data.subtasks:
        create_task_recursive(subtask_data, project_id, db, parent_task_id=task.id)
