import asyncio
import os
from typing import List
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
from sqlalchemy.orm import Session
from schemas import (
    api_schemas as api_schemas,
    employee_model,
    project_model,
    task_model,
)

from services import (
    db_service,
    auth_service,
    employee_service,
    project_service,
    task_service,
)
from utils import password_utils


# from dependency_detection import generate_DAG
# from sklearn.ensemble import RandomForestRegressor
# from sentence_transformers import SentenceTransformer

# AI Models
# encoder = SentenceTransformer("all-MiniLM-L6-v2")
# model = RandomForestRegressor()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
os.makedirs("tables", exist_ok=True)

# ? WebSocket Routing Functions


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    print("Connected to Client")
    tables = ["tasks", "projects", "employees", "companies"]  # Adjust to your table names

    try:
        while True:
            for table in tables:
                # Fetch the table data
                table_data = db_service.fetch_table_data(table)
                print("Sending Table Data")
                # Save the table data to a file
                db_service.save_table_to_file(table, table_data)
            
            # Wait for 1 second before updating again
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")


@app.post("/login", response_model=api_schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(db_service.get_db),
):
    user = employee_service.authenticate_employee(
        email=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = auth_service.create_access_token(data={"sub": user.id})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@app.patch("/set-password/", response_model=api_schemas.MessageResponse)
async def set_password(
    form_data: api_schemas.SetPasswordForm, db: Session = Depends(db_service.get_db)
):
    user = employee_service.load_employee(employee_id=form_data.id, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Link, Employee ID not found",
        )

    if not password_utils.verify_password(
        form_data["temporary_password"], user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid temporary password",
        )

    user.password_hash = password_utils.hash_password(form_data["new_password"])
    db.commit()
    return {"message": "Password created successfully"}


@app.get(
    "/employees/self",
    response_model=employee_model.EmployeeResponse,
    response_model_exclude={"password_hash"},
)
async def get_self_employee(
    db: Session = Depends(db_service.get_db), token: str = Depends(oauth2_scheme)
):
    payload = auth_service.decode_jwt(token)
    employee = employee_service.load_employee(employee_id=payload["sub"], db=db)
    return employee


@app.post("/refresh", response_model=api_schemas.TokenResponse)
async def refresh_token(
    refresh_token_data: api_schemas.RefreshTokenForm,
    db: Session = Depends(db_service.get_db),
):
    refresh_token = refresh_token_data.refresh_token

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    payload = auth_service.decode_jwt(refresh_token)
    employee = employee_service.load_employee(employee_id=payload["sub"], db=db)

    if employee is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = auth_service.create_access_token(data={"sub": employee.id})
    new_refresh_token = auth_service.create_refresh_token(data={"sub": employee.id})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@app.put("/create-new-employee", response_model=api_schemas.MessageResponse)
async def register_employee(
    employee_data: employee_model.EmployeeCreate,
    db: Session = Depends(db_service.get_db),
):
    """API endpoint for registering a new employee"""
    try:
        employee_service.create_employee(employee_data=employee_data, db=db)
        return {"message": "Employee registered successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating employee: {str(e)}"
        )


@app.put("/register-account", response_model=api_schemas.MessageResponse)
async def register_account(
    employee_data: api_schemas.CreateNewAccountForm,
    db: Session = Depends(db_service.get_db),
):
    """API endpoint for registering a new employee"""
    print(employee_data)
    try:
        employee_service.register_account(employee_data=employee_data, db=db)
        return {"message": "Employee registered successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating employee: {str(e)}"
        )
        
@app.get("/employees/get-employees")
async def get_employees(
    db: Session = Depends(db_service.get_db), token: str = Depends(oauth2_scheme)
):
    payload = auth_service.decode_jwt(token)
    manager = employee_service.load_employee(employee_id=payload["sub"], db=db)

    if not manager:
        raise HTTPException(status_code=404, detail="Employee not found")

    employees = employee_service.load_employees(manager, db=db)

    if employees is None:
        raise HTTPException(status_code=404, detail="Employee Search Failed")

    return employees


# @app.put("/employees/{employee_id}", response_model=employee_model.EmployeeResponse, response_model_exclude={"password_hash"})
# async def update_employee(
#     employee_data: employee_model.EmployeeCreate,
#     db: Session = Depends(utils.get_db),
#     token: str = Depends(oauth2_scheme)
# ):
#     """API endpoint for updating an existing employee"""

#     payload = utils.decode_jwt(token)
#     employee_id = payload["sub"]

#     try:
#         employee = (
#             db.query(models.Employee).filter(models.Employee.id == employee_id).first()
#         )
#         if not employee:
#             raise HTTPException(status_code=404, detail="Employee not found")

#         employee.name = employee_data.name
#         employee.email = employee_data.email
#         employee.password_hash = utils.hash_password(employee_data.password)
#         employee.company_id = employee_data.company_id
#         employee.position = employee_data.position
#         employee.manager_id = employee_data.manager_id

#         db.commit()
#         db.refresh(employee)
#         return employee
#     except Exception as e:
#         raise HTTPException(
#             status_code=400, detail=f"Error updating employee: {str(e)}"
#         )


@app.get(
    "/verify-login/",
    response_model=employee_model.EmployeeResponse,
    response_model_exclude={"password_hash"},
)
async def verify_login(
    db: Session = Depends(db_service.get_db), token: str = Depends(oauth2_scheme)
):
    payload = auth_service.decode_jwt(token)
    employee = employee_service.load_employee(employee_id=payload["sub"], db=db)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.put("/projects/create", response_model=project_model.ProjectResponse)
def create_new_project(
    request: project_model.ProjectCreate,
    db: Session = Depends(db_service.get_db),
    token: str = Depends(oauth2_scheme),
):
    auth_service.decode_jwt(token)
    project = project_service.create_project(project=request, db=db)
    return project

@app.put("/projects/{project_id}/edit", response_model=project_model.ProjectResponse)
def edit_project(
    request: project_model.ProjectCreate, 
    project_id: str, 
    db: Session = Depends(db_service.get_db), 
    token: str = Depends(oauth2_scheme)
):
    auth_service.decode_jwt(token)
    project = project_service.load_project(project_id_str=project_id, db=db)
    
    update_data = request.dict(exclude_unset=True)  # Only update provided fields
    for key, value in update_data.items():
        setattr(project, key, value)  # Update only changed fields

    db.commit()
    db.refresh(project)
    return project


@app.get("/projects/get-projects")
async def get_projects_assigned(
    db: Session = Depends(db_service.get_db), token: str = Depends(oauth2_scheme)
):
    payload = auth_service.decode_jwt(token)
    user = employee_service.load_employee(employee_id=payload["sub"], db=db)

    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")

    assigned_projects = project_service.load_projects(employee_id=user.id, db=db)
    # print(assigned_projects)

    # if user.authority_level < 3:
    #     assigned_projects = utils.load_project_tasks(user.employee_id)
    # else:
    #     assigned_projects = utils.load_all_projects()

    if assigned_projects is None:
        raise HTTPException(status_code=404, detail="Project Search Failed")

    return assigned_projects


@app.get("/projects/{project_id}/")
async def get_project_details(
    project_id: str,
    db: Session = Depends(db_service.get_db),
    token: str = Depends(oauth2_scheme),
):
    payload = auth_service.decode_jwt(token)
    employee = employee_service.load_employee(employee_id=payload["sub"], db=db)
    project = project_service.load_project(project_id_str=project_id, db=db)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    display_tasks = task_service.load_project_tasks(
        project_id=project.id, employee_id=employee.id, db=db
    )

    return {"project": project, "tasks": display_tasks}


@app.post("/projects/create-task", response_model=task_model.TaskResponse)
def create_task(
    request: task_model.TaskCreate, 
    db: Session = Depends(db_service.get_db), 
    token: str = Depends(oauth2_scheme)
):
    auth_service.decode_jwt(token)
    project = project_service.load_project(project_id_str=request.project_id, db=db)

    task = task_service.create_task(
        task=request,
        project_id=project.id,
        db=db
    )
    
    task.__dict__["assigned_to"] = request.assigned_to
    print("task: ", task.__dict__)

    return task

@app.post("/projects/{project_id}/batch-create-tasks")
def batch_create_tasks(
    project_id: str,
    tasks: List[task_model.TaskCreateRecursive],
    db: Session = Depends(db_service.get_db),
    token: str = Depends(oauth2_scheme)
):
    # Authenticate user
    user = auth_service.decode_jwt(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Verify project exists
    project = project_service.load_project(project_id_str=project_id, db=db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create each task and its subtasks
    for task_data in tasks:
        task_service.create_task_recursive(task_data, project_id, db)

    return {"message": "Tasks created successfully"}


@app.put("/projects/{project_id}/tasks")
def get_project_tasks(
    project_id: str,
    db: Session = Depends(db_service.get_db),
    token: str = Depends(oauth2_scheme),
):
    payload = auth_service.decode_jwt(token)
    employee = employee_service.load_employee(employee_id=payload["sub"], db=db)
    project = project_service.load_project(project_id_str=project_id, db=db)
    tasks = task_service.load_project_tasks(
        project_id=project.id, employee_id=employee.id, db=db
    )

    if tasks is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return tasks

@app.get("/employees/{employee_id}", response_model=employee_model.EmployeeResponse, response_model_exclude={"password_hash"})
async def get_employee(
    employee_id: str,
    db: Session = Depends(db_service.get_db), token: str = Depends(oauth2_scheme)
):
    payload = auth_service.decode_jwt(token)
    employee = employee_service.load_employee(employee_id=payload["sub"], db=db)
    return employee