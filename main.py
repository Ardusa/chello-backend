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
from fastapi.middleware.cors import CORSMiddleware
from generate_DAG import generate_DAG
from jose import JWTError, jwt  # type: ignore
import base64
import json

# from sklearn.ensemble import RandomForestRegressor
# from sentence_transformers import SentenceTransformer
import numpy as np
from constants import FILE, AUTH
import utils
from models import Database, Task, Project, Employee

# ! Initialization Functions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5001",
        "http://localhost:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# encoder = SentenceTransformer("all-MiniLM-L6-v2")
# model = RandomForestRegressor()
task_history = []
os.makedirs(FILE.PROJECTS_DIR, exist_ok=True)


# ! WebSocket Routing Functions


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


# This is used to login and get the access token plus going to the dashboard
@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = utils.authenticate_employee(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = utils.create_access_token(data={"sub": user.employee_id})
    refresh_token = utils.create_refresh_token(data={"sub": user.employee_id})
    
    # try:
        # print("Access Token: ", access_token, "Expiration", utils.decode_jwt(access_token)["exp"])
        # print("Refresh Token: ", refresh_token, "Expiration", utils.decode_jwt(refresh_token)["exp"])
    # except Exception as e:
    #     print("Error (test): ", str(e))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh/")
async def refresh_token(refresh_token_data: dict):
    refresh_token: str = refresh_token_data.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # print(refresh_token)
    payload = utils.decode_jwt(refresh_token)
    employee_id: str = payload["sub"]
    print("Expiration: ", payload["exp"])

    if employee_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Here you could fetch user data from the database if needed
    new_access_token = utils.create_access_token(data={"sub": employee_id})
    return {"access_token": new_access_token}


@app.post("/register")
async def register_employee(employee_data: dict):
    """API endpoint for registering a new employee"""
    try:
        utils.create_employee(**employee_data)  # Create employee in the database
        return {"message": "Employee registered successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating employee: {str(e)}"
        )


@app.get("/protected/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)
    return {"message": utils.load_employee(payload["sub"])}



@app.post("/projects/create")
def create_new_project(request: dict, token: str = Depends(oauth2_scheme)):
    utils.decode_jwt(token)
    project = utils.create_project(**request)
    return {"message": "Project created successfully", "project_id": project.project_id}


# This is used to display stuff on the dashboard
@app.get("/projects/get_projects")
async def dashboard(token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)

    user = utils.load_employee(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")

    if (user.authority_level < 3):
        assigned_projects = utils.load_assigned_projects(user.employee_id)
    
    else:
        assigned_projects = utils.load_all_projects()
    
    if assigned_projects is None:  # Only raise 404 if the result is None
        raise HTTPException(status_code=404, detail="No projects found")
    
    # Return the projects in a dictionary with a descriptive key
    return {"assigned_projects": assigned_projects}



# This is used to display stuff on the project page
@app.get("/projects/{project_id}/")
async def get_tasks(project_id: str, token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)

    project = utils.load_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    employee = utils.load_employee(payload["sub"])
    if employee.authority_level < 3 and employee.employee_id:
        display_tasks = utils.load_project_tasks(
            project_id=project_id, employee_id=payload["sub"]
        )
    else:
        display_tasks = utils.load_project_tasks(project_id=project_id)
    if not display_tasks:
        raise HTTPException(status_code=404, detail="No tasks found")

    return {"project": project, "tasks": display_tasks}


@app.get("/projects/{project_id}/tasks")
def get_project_tasks(project_id: str, token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)
    tasks = utils.load_project_tasks(project_id, payload["sub"])
    if tasks is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project_id": project_id, "tasks": tasks}


# @app.post("/register/")
# async def create_advanced_employee(employee_data):
#     utils.create_employee(employee_data)


# # ! WebSocket Endpoint


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()  # Accept the WebSocket connection
#     print("Connected to Client")
#     try:
#         while True:
#             # Code for handling the connection or processing logic
#             # No sleep, so the server can immediately process further tasks
#             pass
#     except WebSocketDisconnect:
#         print("WebSocket disconnected")


# # ! Employee Functions

# # def load_employees() -> dict[str, models.Employee]:
# #     try:
# #         with open(FILE.EMPLOYEES_FILE, "r") as f:
# #             data = json.load(f)
# #             # Convert the dictionary back into Employee instances
# #             return {
# #                 emp_id: models.Employee(**employee_data)
# #                 for emp_id, employee_data in data.items()
# #             }
# #     except (FileNotFoundError, json.JSONDecodeError):
# #         return {}


# # def save_employees(employees: dict[str, models.Employee]):
# #     employees_dict = {id: employee.dict() for id, employee in employees.items()}
# #     with open(FILE.EMPLOYEES_FILE, "w") as f:
# #         json.dump(employees_dict, f, indent=4)


# @app.post("/add_employee/")
# async def add_employee(
#     employee_id: str,
#     full_name: str,
#     email: str,
#     position: int,
#     password: str,
#     token: str = Depends(oauth2_scheme),
# ):
#     try:
#         payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#         admin_id = payload["sub"]

#         utils.create_employee(employee_id, full_name, email, position, password)

#         # employees = load_employees()
#         # if employees[admin_id].position < 3:
#         #     raise HTTPException(
#         #         status_code=403, detail="Only level 3+ can add employees"
#         #     )
#         # employees[employee_id] = {
#         #     "id": employee_id,
#         #     "full_name": full_name,
#         #     "email": email,
#         #     "position": position,
#         #     "password": password,
#         # }
#         # save_employees(employees)
#         return {"message": "Employee added successfully"}
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# @app.post("/change-password/")
# async def change_password(
#     employee_id: str,
#     old_password: str,
#     new_password: str,
#     token: str = Depends(oauth2_scheme),
# ):
#     try:
#         payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#         user_id = payload["sub"]
#         employees = load_employees()
#         if user_id != employee_id:
#             raise HTTPException(
#                 status_code=403, detail="You can only change your own password"
#             )
#         user = employees.get(employee_id)
#         if not user or not user.verify_password(old_password):
#             raise HTTPException(status_code=400, detail="Invalid old password")
#         user.password = new_password
#         save_employees(employees)
#         return {"message": "Password changed successfully"}
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# @app.post("/forgot_password/")
# async def forgot_password(email: str):
#     employees = load_employees()
#     user = next((emp for emp in employees.values() if emp.email == email), None)
#     if not user:
#         raise HTTPException(status_code=404, detail="Email not registered")

#     try:
#         send_email(
#             to_email=email,
#             subject="Your Password",
#             body=f"Hello {user.full_name},\n\nYour password is: {user.password}",
#         )
#         return {"message": f"Your password has been sent to {email}!"}
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to send email")


# # ! Project Functions


# @app.get("/get_projects/")
# async def get_projects(token: str = Depends(oauth2_scheme)):
#     # print(token)
#     try:
#         # print("Token: ", token)
#         payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#         employee_id = payload["sub"]
#         print("Employee ID: ", employee_id)
#         employees = load_employees()
#         if employee_id not in employees:
#             raise HTTPException(status_code=404, detail="Employee not found")
#         assigned_projects = [
#             pid
#             for pid in os.listdir(FILE.PROJECTS_DIR)
#             if employee_id in load_project(pid).get("employees", [])
#         ]
#         return {"message": assigned_projects}
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


# # ! Model Functions


# def load_model():
#     """Load the trained model data from a JSON file."""
#     if not os.path.exists(FILE.MODEL_DATA_FILE):
#         return

#     with open(FILE.MODEL_DATA_FILE, "r") as f:
#         model_data = json.load(f)

#     X = np.array(model_data["X"])
#     y = np.array(model_data["y"])

#     if len(X) > 0 and len(y) > 0:
#         model.fit(X, y)
#         print("Pre-trained model loaded successfully.")


# def save_model():
#     """Save the trained model data to a JSON file."""
#     if not task_history:
#         return
#     X = np.array([extract_features(task) for task in task_history])
#     y = np.array([task.actual_hours.total_seconds() / 3600 for task in task_history])
#     model.fit(X, y)

#     model_data = {"X": X.tolist(), "y": y.tolist()}

#     with open(FILE.MODEL_DATA_FILE, "w") as f:
#         json.dump(model_data, f)


# @app.post("/train_model/")
# async def train_model(token: str = Depends(oauth2_scheme)):
#     try:
#         jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     if not task_history:
#         raise HTTPException(status_code=400, detail="No training data available")
#     X = np.array([extract_features(task) for task in task_history])
#     y = np.array([task.actual_hours.total_seconds() / 3600 for task in task_history])
#     model.fit(X, y)
#     return {"message": "Model trained successfully"}


# @app.post("/predict_time/")
# async def predict_time(task: models.Task, token: str = Depends(oauth2_scheme)):
#     try:
#         jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     features = extract_features(task).reshape(1, -1)
#     predicted_hours = model.predict(features)[0]
#     return {"message": predicted_hours}


# def extract_features(task: models.Task):
#     text_features = encoder.encode(task.name + " " + task.description)
#     dependency_count = len(task.dependencies)
#     return np.hstack((text_features, [dependency_count]))


# # ! Task Functions

# @app.post("/{project_id}/create_task/")
# async def create_task(project_id: str, task: models.Task, token: str = Depends(oauth2_scheme)):
#     try:
#         jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     utils.append_task(task, project_id)
#     # project = utils.load_project(project_id)
#     # if not project:
#     #     raise HTTPException(status_code=404, detail="Project not found")

#     # project["tasks"].append(task.dict())
#     # utils.save_project(project_id, project)
#     return {"message": "Task created successfully"}


# @app.get("/{project_id}/")
# async def get_tasks(project_id: str, token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#         user = payload["sub"]

#         project = utils.load_project(project_id=project_id)
#         if (user not in )
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return {"message": utils.load_tasks(project_id=project_id)}


# @app.get("/generate_test_data/")
# async def generate_test_data(token: str = Depends(oauth2_scheme)):
#     try:
#         jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     test_tasks = {
#         "Gather Requirements": "Identify and document all functional and non-functional requirements before starting development.",
#         "Design Database Schema": "Define tables, relationships, and constraints before implementing the backend.",
#         "Develop Backend API": "Implement the server-side logic and endpoints after designing the database schema.",
#         "Develop Frontend UI": "Create user interface components after the backend API is functional.",
#         "Implement Authentication System": "Integrate user authentication after backend development is completed.",
#         "Write Unit Tests": "Develop unit tests for core modules after backend and frontend development.",
#         "Perform Integration Testing": "Test interactions between frontend and backend after unit testing is completed.",
#         "Deploy Application": "Deploy the application after passing integration tests.",
#         "Monitor System Performance": "Continuously monitor application performance after deployment.",
#     }

#     test_dependencies = {
#         "Gather Requirements": [],
#         "Design Database Schema": ["Gather Requirements"],
#         "Develop Backend API": ["Design Database Schema"],
#         "Develop Frontend UI": ["Develop Backend API"],
#         "Implement Authentication System": ["Develop Backend API"],
#         "Write Unit Tests": ["Develop Backend API", "Develop Frontend UI"],
#         "Perform Integration Testing": ["Write Unit Tests"],
#         "Deploy Application": ["Perform Integration Testing"],
#         "Monitor System Performance": ["Deploy Application"],
#     }

#     tasks_list = []
#     for task_name, task_description in test_tasks.items():
#         tasks_list.append(
#             models.Task(
#                 name=task_name,
#                 description=task_description,
#                 dependencies=test_dependencies.get(task_name, []),
#                 start_date=datetime.now(),
#                 status=models.TaskStatus.OPEN,
#             )
#         )

#     for task_data in tasks_list:
#         task = models.Task(**task_data)
#         await create_task(task)

#     return {"tasks": tasks}


# @app.post("/add_completed_task/")
# async def add_completed_task(task: models.Task, token: str = Depends(oauth2_scheme)):
#     try:
#         jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     if task.status != models.TaskStatus.COMPLETED or not task.actual_hours:
#         raise HTTPException(
#             status_code=400, detail="Task must be completed with actual hours"
#         )
#     task_history.append(task)
#     return {"message": "Task added to training data"}


# def encoded_image():
#     """Reads the DAG PNG file and converts it to a Base64 string"""
#     try:
#         with open("Assets/Graphs/DAG_Visualization.png", "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode("utf-8")
#     except FileNotFoundError:
#         return "Error: Image file not found."


# @app.get("/generate_DAG/")
# async def generate_DAG_endpoint(token: str = Depends(oauth2_scheme)):
#     try:
#         jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     dependencies = {task.name: task.dependencies for task in tasks}
#     await generate_DAG(dependencies, "DAG_Visualization")
#     return {"message": encoded_image()}


# # ! Initialization Functions

# # Load model on startup
# load_model()

# # uvicorn.run("main:app", host=LAN_host, port=8000, reload=True)
