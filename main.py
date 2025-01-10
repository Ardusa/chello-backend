from datetime import datetime, timedelta
import os
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
from generate_DAG import generate_DAG

from jose import JWTError, jwt
import base64
import json
import models

app = FastAPI()

# ! Authentication stuff
SECRET_KEY = "CHELLO"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    """Model to store access token and token type."""

    access_token: str
    """Access token for authentication."""
    token_type: str
    """Token type (Bearer)."""


EMPLOYEES_FILE = "employees.json"
PROJECTS_DIR = "projects/"

# Ensure projects directory exists
os.makedirs(PROJECTS_DIR, exist_ok=True)


def load_employees():
    try:
        with open(EMPLOYEES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_employees(employees):
    with open(EMPLOYEES_FILE, "w") as f:
        json.dump(employees, f, indent=4)


def load_project(project_id):
    try:
        with open(f"{PROJECTS_DIR}{project_id}.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_project(project_id, project_data):
    with open(f"{PROJECTS_DIR}{project_id}.json", "w") as f:
        json.dump(project_data, f, indent=4)


# Initialize default admin if empty
employees = load_employees()
if not employees:
    admin = models.Employee(
        id="admin",
        full_name="Admin User",
        email="admin@example.com",
        position=3,
        password="admin",
    )
    admin.hash_password()
    employees[admin.id] = admin
    save_employees(employees)

print("Employee and Project JSON storage system initialized.")

employees: dict[str, models.Employee] = {
    "ardusa": models.Employee(
        id="ardusa", full_name="Ankur Desai", email="ardusa05@gmail.com", position=3
    ),
    "school":models.Employee(
        id="school",
        full_name="Michigan State",
        email="desaia11@msu.edu",
        password="chello",
    ),
}


def authenticate_user(employee_id: str, password: str):
    employees = load_employees()
    user = employees.get(employee_id)
    if not user or not models.pwd_context.verify(password, user["password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["id"]}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/add_employee/")
async def add_employee(employee_id: str, full_name: str, email: str, position: int, password: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload["sub"]
        employees = load_employees()
        if employees[admin_id]["position"] != 3:
            raise HTTPException(status_code=403, detail="Only level 3 admins can add employees")
        employees[employee_id] = {
            "id": employee_id,
            "full_name": full_name,
            "email": email,
            "position": position,
            "password": models.pwd_context.hash(password),
        }
        save_employees(employees)
        return {"message": "Employee added successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/get_projects/")
async def get_projects(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id = payload["sub"]
        employees = load_employees()
        if employee_id not in employees:
            raise HTTPException(status_code=404, detail="Employee not found")
        assigned_projects = [pid for pid in os.listdir(PROJECTS_DIR) if employee_id in load_project(pid).get("employees", [])]
        return {"projects": assigned_projects}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
async def create_task(task: models.Task, token: str = Depends(oauth2_scheme)):
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
            "status": models.TaskStatus.OPEN,
        }
        tasks_list.append(task_data)

    for task_data in tasks_list:
        task = models.Task(**task_data)
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
