from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
import smtplib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Employee, Project, Task, Company, task_employee_association, Base
from constants import EMAIL, AUTH, DATABASE
from collections import OrderedDict
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the database engine
engine = create_engine(DATABASE.URL, connect_args={"check_same_thread": False})

# Define the sessionmaker for interacting with the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Database utility functions


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Functions to interact with SQLAlchemy


def create_employee(employee: dict) -> Employee:
    db = next(get_db())

    # Check if manager_id is real
    if (
        employee.manager_id
        and not db.query(Employee).filter(Employee.id == employee.manager_id).first()
    ):
        raise HTTPException(status_code=400, detail="Manager ID does not exist")

    # Check if company_id is real
    if (
        employee.company_id
        and not db.query(Company).filter(Company.id == employee.company_id).first()
    ):
        raise HTTPException(status_code=400, detail="Company ID does not exist")

    plain_password = employee.pop("password")
    employee["password_hash"] = hash_password(plain_password)

    new_employee = Employee(**employee)

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


def load_employee(
    employee_id: Optional[int] = None , email: Optional[str] = None
) -> Optional[Employee]:
    db = get_db()
    if employee_id:
        return db.query(Employee).filter(Employee.id == employee_id).first()
    if email:
        return db.query(Employee).filter(Employee.email == email).first()
    return None


def create_project(project: Project, order: int) -> Project:
    db = Depends(get_db)
    new_project = Project(**project.dict(), order=order)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def load_project(project_id: int) -> Optional[Project]:
    db = get_db()
    return db.query(Project).filter(Project.id == project_id).first()


def create_task(task: Task, project_id: int, parent_task_id: Optional[int] = None):
    db = get_db()
    db_task = Task(**task.dict(), project_id=project_id, parent_task_id=parent_task_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def load_task(task_id: int):
    db = get_db()
    return db.query(Task).filter(Task.id == task_id).first()


def load_project_tasks(employee_id=None, project_id=None):
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

    db = get_db()
    query = db.query(Task)

    if employee_id:
        query = query.join(task_employee_association).filter(
            task_employee_association.c.employee_id == employee_id
        )

    if project_id:
        query = query.filter(Task.project_id == project_id)

    # Order tasks by the order column
    query = query.order_by(Task.order)

    tasks = query.all()

    def build_task_dict(task):
        """Recursively build an ordered dictionary of tasks to their subtasks."""
        task_dict = OrderedDict({task: []})
        for subtask in sorted(task.subtasks, key=lambda t: t.order):
            if not employee_id or employee_id in [emp.id for emp in subtask.employees]:
                task_dict[task].append(build_task_dict(subtask))
        return task_dict

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


def authenticate_employee(email: str, password: str):
    employee: Employee = load_employee(employee_id=None, email=email)
    if not employee:
        print("Employee account not found: ", email)
        return False

    passGood = verify_password(
        plain_password=password, hashed_password=employee.password_hash
    )
    # passGood = employee.verify_password(password=password)
    if not passGood:
        print("Password incorrect: ", password)
        return False

    return employee


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=AUTH.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta  # Use timezone-aware datetime
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, AUTH.SECRET_KEY, algorithm=AUTH.ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=AUTH.REFRESH_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta  # Use timezone-aware datetime
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, AUTH.SECRET_KEY, algorithm=AUTH.ALGORITHM)


def decode_jwt(token: str) -> dict:
    """
    Decode a JWT token and return the payload.

    Args:
    - token (str): The JWT token to decode.

    Returns:
    - dict: The decoded payload.

    Raises:
    - HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_password(form_data: dict):
    user: Employee = load_employee(employee_id=form_data["id"])

    if not user and verify_password(
        form_data["temporary_password"], user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Link, Employee ID not found",
        )

    user.password_hash = hash_password(form_data["new_password"])


def send_email(to_email: str, subject: str, body: str):
    """Send an email to the given email address with the given subject and body, email is sent using the Chello Team email address, signature is appended to the body automatically."""
    msg = MIMEText(body + EMAIL.SIGNATURE)
    msg["Subject"] = subject
    msg["From"] = EMAIL.EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL.SMTP_SERVER, EMAIL.SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL.EMAIL_ADDRESS, EMAIL.EMAIL_PASSWORD)
        server.sendmail(EMAIL.EMAIL_ADDRESS, to_email, msg.as_string())


def display_current_day_time() -> str:
    now = datetime.now()
    day_of_week = now.strftime("%A")  # Full weekday name
    hour = now.strftime("%H")  # Hour (24-hour clock)
    minute = now.strftime("%M")  # Minute
    second = now.strftime("%S")  # Second
    return f"{day_of_week}, {hour}:{minute}:{second}, {now.strftime('%Y-%m-%d')}"
