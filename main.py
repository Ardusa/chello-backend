from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from enum import Enum
from generate_DAG import generate_DAG
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
import base64
import uvicorn

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "ankur": {
        "username": "ankur",
        "password": pwd_context.hash("chello"),  # Store hashed password
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return False
    return User(username=username)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
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


class TaskStatus(Enum):
    """Working status of task."""

    OPEN = "Open"
    """Task is open and ready to be started."""
    IN_PROGRESS = "In Progress"
    """Task is currently being worked on."""
    COMPLETED = "Completed"
    """Task has been completed."""


# Task Model
class Task(BaseModel):
    name: str
    description: str
    dependencies: list[str] = []
    subtasks: list[str] = []
    status: TaskStatus = TaskStatus.OPEN
    start_date: datetime | None = None
    estimated_hours: int | None = None
    calculated_hours: int | None = None
    end_date: datetime | None = None


tasks: list[Task] = []
"""Store tasks and dependencies (Initially empty, will be updated dynamically)"""

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


# # API Endpoint: Get Schedule
# @app.get("/schedule/")
# def get_schedule():
#     return schedule_tasks()


def encode_image():
    """Reads the DAG PNG file and converts it to a Base64 string"""
    try:
        with open("Assets/Graphs/DAG_Visualization.png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return "Error: Image file not found."

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