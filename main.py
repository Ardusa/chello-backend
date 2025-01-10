from datetime import datetime, timedelta
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from enum import Enum
from generate_DAG import generate_DAG
from prioritization_engine import (
    calculate_time_estimate,
    calculate_time_of_completion,
    calculate_efficiency,
)
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, List
import base64
import uvicorn

SECRET_KEY = "CHELLO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskStatus(Enum):
    """Working status of task."""

    OPEN = "OPEN"
    """Task is open and ready to be started."""
    IN_PROGRESS = "IN_PROGRESS"
    """Task is currently being worked on."""
    COMPLETED = "COMPLETED"
    """Task has been completed."""


class Employee(BaseModel):
    """Employee model to store employee details."""

    id: str
    """Unique identifier for the employee (username or employee ID)."""
    full_name: str
    """Full name of the employee."""
    email: str
    """Email address of the employee."""
    position: Optional[int] = 1
    """Position of the employee in the organization, 1 for base level, 2 for manager, 3 for admin."""
    enabled: Optional[bool] = True
    """Flag to enable or disable the employee account."""
    efficiency_score: Optional[float] = 1.0  # Default efficiency score of 100%
    """Efficiency score of the employee (default: 100%)."""
    password: str = "password"
    """Password for the employee account."""

    def __init__(self, **data):
        super().__init__(**data)
        self.password = pwd_context.hash(self.password)


# Task Model
class Task(BaseModel):
    """Task model to store task details."""

    name: str
    """Name of the task."""
    description: str
    """Description of the task."""
    dependencies: List[str] = []
    """List of tasks that this task depends on."""
    subtasks: List[str] = []
    """List of tasks that are completed only as part of this task."""
    status: TaskStatus = TaskStatus.OPEN
    """Current status of the task."""
    start_date: Optional[datetime] = None
    """Date when the task was started."""
    estimated_hours: Optional[int] = None
    """User estimated time required to complete the task."""
    calculated_hours: Optional[timedelta] = None
    """Calculated estimate of time required to complete the task."""
    actual_hours: Optional[timedelta] = None
    """Actual time taken to complete the task."""
    end_date: Optional[datetime] = None
    """Date when the task was completed."""
    users_assigned: List[Employee] = []
    """List of employees assigned to the task."""

    def __init__(self, **data):
        super().__init__(**data)
        if self.status is TaskStatus.COMPLETED:
            self.actual_hours = self.end_date - self.start_date
        if self.start_date is None:
            self.start_date = datetime.now()
        if self.calculated_hours is None:
            self.calculated_hours = calculate_time_estimate(self).calculated_hours
        if self.end_date is None:
            self.end_date = None


tasks: list[Task] = []
"""Store tasks and dependencies (Initially empty, will be updated dynamically)"""

# fake_users_db = {
#     "ankur": {
#         "username": "ankur",
#         "password": pwd_context.hash("chello"),  # Store hashed password
#     }
# }

employees: dict[str, Employee] = {
    "ardusa": Employee(
        id="ardusa", full_name="Ankur Desai", email="ardusa05@gmail.com", position=3
    ),
    "school": Employee(
        id="school",
        full_name="Michigan State",
        email="desaia11@msu.edu",
        password="chello",
    ),
}


def authenticate_user(username: str, password: str):
    user: Employee = employees.get(username)

    if not user or not pwd_context.verify(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"message": f"Hello {payload['sub']}"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Run server only if this script is the main entry point
if __name__ == "__main__":
    local_host = "127.0.0.1"
    LAN_host = "192.168.0.80"
    # uvicorn.run("main:app", host=LAN_host, port=8000, reload=True)


@app.post("/create_task/")
async def create_task(task: Task, token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    tasks.append(task)
    return {"task": task}


@app.get("/get_tasks/")
async def get_tasks(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return tasks


@app.get("/generate_test_data/")
async def generate_test_data(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    global tasks

    test_tasks = {
        "Gather Requirements": "Identify and document all functional and non-functional requirements before starting development.",
        "Design Database Schema": "Define tables, relationships, and constraints before implementing the backend.",
        "Develop Backend API": "Implement the server-side logic and endpoints after designing the database schema.",
        "Develop Frontend UI": "Create user interface components after the backend API is functional.",
        "Implement Authentication System": "Integrate user authentication after backend development is completed.",
        "Write Unit Tests": "Develop unit tests for core modules after backend and frontend development.",
        "Perform Integration Testing": "Test interactions between frontend and backend after unit testing is completed.",
        "Deploy Application": "Deploy the application after passing integration tests.",
        "Monitor System Performance": "Continuously monitor application performance after deployment.",
    }

    test_dependencies = {
        "Gather Requirements": [],
        "Design Database Schema": ["Gather Requirements"],
        "Develop Backend API": ["Design Database Schema"],
        "Develop Frontend UI": ["Develop Backend API"],
        "Implement Authentication System": ["Develop Backend API"],
        "Write Unit Tests": ["Develop Backend API", "Develop Frontend UI"],
        "Perform Integration Testing": ["Write Unit Tests"],
        "Deploy Application": ["Perform Integration Testing"],
        "Monitor System Performance": ["Deploy Application"],
    }

    tasks_list = []
    for task_name, task_description in test_tasks.items():
        task_data = {
            "name": task_name,
            "description": task_description,
            "dependencies": test_dependencies.get(task_name, []),
            "start_date": datetime.now(),
            "status": TaskStatus.OPEN,
        }
        tasks_list.append(task_data)

    for task_data in tasks_list:
        task = Task(**task_data)
        await create_task(task)

    return {"tasks": tasks}


def encoded_image():
    """Reads the DAG PNG file and converts it to a Base64 string"""
    try:
        with open("Assets/Graphs/DAG_Visualization.png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return "Error: Image file not found."


@app.get("/generate_DAG/")
async def generate_DAG_endpoint(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    dependencies = {task.name: task.dependencies for task in tasks}
    await generate_DAG(dependencies, "DAG_Visualization")
    return {"image": encoded_image()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    print("Connected to Client")
    try:
        while True:
            # Code for handling the connection or processing logic
            # No sleep, so the server can immediately process further tasks
            pass
    except WebSocketDisconnect:
        print("WebSocket disconnected")
