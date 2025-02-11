import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from schemas import project_model
from services import get_db, task_service
from sqlalchemy import func
from collections import OrderedDict
from typing import Optional, Dict
from models import Project, Task, task_employee_association


def create_project(
    project: project_model.ProjectCreate, db: Session = Depends(get_db)
) -> Project:
    project = Project(
        company_id=uuid.UUID(project.company_id),
        name=project.name,
        description=project.description,
        project_manager=uuid.UUID(project.project_manager),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def load_project(
    project_id_str: str = None,
    project_id: uuid.UUID = None,
    db: Session = Depends(get_db),
) -> Optional[Project]:
    if not project_id:
        project_id = uuid.UUID(project_id_str)

    return db.query(Project).filter(Project.id == project_id).first()


def load_projects(
    employee_id: uuid.UUID, db: Session = Depends(get_db)
) -> Dict[int, Project]:
    # Query to get the count of tasks per project for the given employee
    task_counts = (
        # db.query(Project, func.count(Task.id).label("task_count"))
        db.query(Project.id, func.count(Task.id).label("task_count"))
        .outerjoin(Task, Project.id == Task.project_id)
        .outerjoin(
            task_employee_association, Task.id == task_employee_association.c.task_id
        )
        .filter(
            (task_employee_association.c.employee_id == employee_id)
            | (Project.project_manager == employee_id)
            | (Task.id.is_(None))
        )
        .group_by(Project.id)
        .order_by(func.count(Task.id).desc())
        .all()
    )

    # Create an ordered dictionary of projects based on the task count
    projects = OrderedDict()
    for project_id, task_count in task_counts:
        if task_count == 0:
            project = load_project(project_id=project_id, db=db)
            if project.project_manager == employee_id:
                projects[project_id] = project.__dict__

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project with ID {project_id} not found.")

        tasks = task_service.load_project_tasks(
            employee_id=employee_id, project_id=project_id, db=db
        )

        def get_task_count(
            project: OrderedDict[uuid.UUID, OrderedDict[uuid.UUID, any]],
        ) -> int:
            count = 0
            for parent_task_id, child_tasks in project.items():
                parent_task = task_service.load_task(str(parent_task_id), db)
                master_task_count = 0

                if len(child_tasks) > 0:
                    for child_id, child_child_task_id_or_dict in child_tasks.items():
                        print("Child ID: " + str(child_id))
                        child_task = task_service.load_task(str(child_id), db)
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
