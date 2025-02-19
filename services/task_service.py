from collections import OrderedDict
from typing import Optional
import uuid

from models import Task, Project
from sqlalchemy.orm import Session
from fastapi import Depends
from schemas import task_model
from .db_service import get_db
from .account_service import load_account
from models import task_account_association


def create_task(
    task: task_model.TaskCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new task in the database. The task must be assigned to a project.
    """
    new_task = Task(
        name=task.name,
        description=task.description,
        order=task.order,
    )

    # load_project(project_id=project_id, db=db)
    project_id = uuid.UUID(task.project_id)
    from .project_service import load_project

    load_project(project_id=project_id, db=db)
    new_task.project_id = project_id

    assigned_to_id = uuid.UUID(task.assigned_to)
    load_account(account_id=assigned_to_id, db=db)
    new_task.assigned_to = assigned_to_id

    if task.parent_task_id:
        parent_task_id = uuid.UUID(task.parent_task_id)
        load_task(task_id=parent_task_id, db=db)
        new_task.parent_task_id = parent_task_id

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    db.execute(
        task_account_association.insert().values(
            task_id=new_task.id, account_id=new_task.assigned_to
        )
    )
    db.commit()

    return new_task


def load_task(
    task_id: Optional[uuid.UUID] = None,
    task_id_str: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Task:
    """
    This function is used to load a task from the database. It will throw an error if the query returns no results.
    """

    if task_id_str:
        task_id = uuid.UUID(task_id_str)

    query = db.query(Task)

    if task_id:
        query = query.filter(Task.id == task_id).first()

    if not query or not task_id:
        raise ValueError("Task not found: ", task_id)

    return query


# Code for creating the dictionary
def build_task_dict(
    project: OrderedDict[uuid.UUID, OrderedDict[uuid.UUID, any]], task: Task
):
    """Recursively build an ordered dictionary of tasks to their subtasks."""

    def sort_recursive_dict(d: OrderedDict):
        """Recursively sort an OrderedDict by the 'order' attribute of the keys."""
        sorted_dict = OrderedDict()
        for key, value in sorted(
            d.items(),
            key=lambda item: item[1].order if isinstance(item[1], Task) else 0,
        ):
            if isinstance(value, OrderedDict):
                sorted_dict[key] = sort_recursive_dict(value)
            else:
                sorted_dict[key] = value
        return sorted_dict

    if not task.parent_task_id:
        project[task.id] = OrderedDict()

    else:

        def recursive_insert(project, task):
            for id, value in project.items():
                if task.parent_task_id == id:
                    if isinstance(value, OrderedDict):
                        value[task.id] = OrderedDict()
                        return True
                elif isinstance(value, OrderedDict):
                    if recursive_insert(value, task):
                        return True
            return False

        if not recursive_insert(project, task):
            # Add the parent task to the project dictionary if not found
            project[task.parent_task_id] = OrderedDict()
            project[task.parent_task_id][task.id] = OrderedDict()

    # ! Does not work

    # sort_recursive_dict(project)
    return project


def load_project_tasks(
    account_id=None,
    project_id=None,
    db: Session = Depends(get_db),
):
    """
    Get all tasks relevant to a specific account for a specific project.

    Parameters:
    account_id (UUID, optional): The ID of the account. If provided, the function will filter tasks to only include those assigned to this account.
    project_id (UUID, optional): The ID of the project. If provided, the function will filter tasks to only include those within this project.

    Returns:
    dict:
        - If both account_id and project_id are provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
        - If only account_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.
        - If only project_id is provided, returns a dictionary where the keys are tasks and the values are lists of their subtasks.
        - If neither account_id nor project_id is provided, returns a dictionary where the keys are project IDs and the values are dictionaries. Each inner dictionary has tasks as keys and lists of their subtasks as values.

    The function recursively builds the dictionary to include all subtasks and their subtasks, and so on. If account_id is provided, only subtasks assigned to the account are included.
    """

    query = db.query(Task)

    if account_id and project_id:
        # If the project specified happens to be managed by the employee, return all tasks in the project
        if project_id in [
            pid
            for (pid,) in db.query(Project.id)
            .filter(Project.project_manager == account_id)
            .all()
        ]:
            query = query.filter(Task.project_id == project_id)

        # If the account is not a project manager, check if the account is assigned to any tasks
        else:
            query = (
                db.query(Task)
                .filter(Task.project_id == project_id)
                .filter(Task.assigned_to == account_id)
            )

    elif account_id and not project_id:
        query = query.filter(Task.assigned_to == account_id)

    elif not account_id and project_id:
        query = query.filter(Task.project_id == project_id)

    query = query.order_by(Task.project_id, Task.parent_task_id, Task.order)

    tasks = query.all()

    if account_id and project_id:
        # Order the project based on the accounts role in the project.
        project = OrderedDict()
        for task in tasks:
            project.update(build_task_dict(project, task))
        return project

    elif account_id and not project_id:
        # Separate tasks into each project the account is part of
        projects = OrderedDict()
        for task in tasks:
            if task.project_id not in projects:
                projects[task.project_id] = OrderedDict()
            projects[task.project_id].update(
                build_task_dict(projects[task.project_id], task)
            )
        return projects

    elif not account_id and project_id:
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


def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a task from the database. This will also delete all subtasks of the task.
    """
    db.query(Task).filter(Task.parent_task_id == task_id).delete()
    db.query(Task).filter(Task.id == task_id).delete()
    db.query(task_account_association).filter(
        task_account_association.c.task_id == task_id
    ).delete()
    db.commit()
    return True
