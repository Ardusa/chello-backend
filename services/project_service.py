import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from schemas import project_model
from .db_service import get_db
from .account_service import load_account
from .company_service import load_company
from .task_service import load_task, load_project_tasks, delete_task
from sqlalchemy import func
from collections import OrderedDict
from models import Project, Task, task_account_association


def create_project(
    project: project_model.ProjectCreate, db: Session = Depends(get_db)
) -> Project:
    """
    Create a new project in the database. 
    """
    new_project = Project(
        name=project.name,
        description=project.description,
    )
    
    project_manager_id = uuid.UUID(project.project_manager)
    load_account(account_id=project_manager_id, db=db)
    new_project.project_manager = project_manager_id
    
    company_id = uuid.UUID(project.company_id)
    load_company(company_id=company_id, db=db)
    new_project.company_id = company_id
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def load_project(
    project_id_str: str = None,
    project_id: uuid.UUID = None,
    db: Session = Depends(get_db),
) -> Project:
    """
    This function is used to load a project from the database. It will throw an error if the query returns no results.
    """
    if project_id_str:
        project_id = uuid.UUID(project_id_str)

    query = db.query(Project)
    
    if project_id:
        query = query.filter(Project.id == project_id).first()

    if not query:
        raise ValueError(
            "Project not found: ", project_id
        )
    
    return query


def load_projects(
    account_id: uuid.UUID, db: Session = Depends(get_db)
):
    """
    Load all projects that the account is assigned to or is managing.
    """
    task_counts = (
        db.query(Project.id, func.count(Task.id).label("task_count"))
        .outerjoin(Task, Project.id == Task.project_id)
        .outerjoin(
            task_account_association, Task.id == task_account_association.c.task_id
        )
        .filter(
            (task_account_association.c.account_id == account_id)
            | (Project.project_manager == account_id)
        )
        .group_by(Project.id)
        .order_by(func.count(Task.id).desc())
        .all()
    )

    print("Task counts: " + str(task_counts))
    print(db.query(Task).filter(Task.assigned_to == account_id).all())

    # Create an ordered dictionary of projects based on the task count
    projects = OrderedDict()
    for project_id, task_count in task_counts:
        if task_count == 0:
            project = load_project(project_id=project_id, db=db)
            if project.project_manager == account_id:
                projects[project_id] = project.__dict__

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project with ID {project_id} not found.")

        tasks = load_project_tasks(
            account_id=account_id, project_id=project_id, db=db
        )

        def get_task_count(
            project: OrderedDict[uuid.UUID, OrderedDict[uuid.UUID, any]],
        ) -> int:
            count = 0
            for parent_task_id, child_tasks in project.items():
                parent_task = load_task(str(parent_task_id), db)
                master_task_count = 0

                if len(child_tasks) > 0:
                    for child_id, child_child_task_id_or_dict in child_tasks.items():
                        print("Child ID: " + str(child_id))
                        child_task = load_task(str(child_id), db)
                        child_completion_count = 0
                        if isinstance(
                            child_child_task_id_or_dict, OrderedDict
                        ):  # Will always be true
                            if len(child_child_task_id_or_dict) > 0:
                                child_completion_count += get_task_count(
                                    child_child_task_id_or_dict
                                )
                                print(
                                    "Child completion count: "
                                    + str(child_completion_count)
                                )
                            else:  # If there are no subtasks
                                print(
                                    "Task: "
                                    + child_task.name
                                    + " completed: "
                                    + str(child_task.completed)
                                )
                                if not child_task.completed:
                                    child_completion_count += 1

                        if not child_completion_count == 0:
                            master_task_count += 1
                        else:
                            child_task.completed = True
                else:
                    if not parent_task.completed:
                        master_task_count += 1

                if master_task_count > 0:
                    count += 1
                    parent_task.completed = False
                else:
                    parent_task.completed = True

            return count

        task_count = get_task_count(tasks)
        project_dict = project.__dict__
        project_dict["tasks_remaining"] = task_count
        projects[project_id] = project_dict

    return projects


def update_project(
    project_id: uuid.UUID,
    project: project_model.ProjectCreate,
    db: Session = Depends(get_db),
) -> Project:
    db_project = db.query(Project).filter(Project.id == project_id).first()
    db_project.name = project.name
    db_project.description = project.description
    db_project.project_manager = uuid.UUID(project.project_manager)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    for task in tasks:
        delete_task(task.id, db)
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        
    db.query(Project).filter(Project.id == project_id).delete()
    db.commit()
    return True
