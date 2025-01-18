from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from models import Project
from services import get_db


def create_project(project: Project, db: Session = Depends(get_db)) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def load_project(project_id: int, db: Session = Depends(get_db)) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()
