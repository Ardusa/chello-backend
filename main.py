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
import uvicorn
import database.utils as utils

# from dependency_detection import generate_DAG
# from sklearn.ensemble import RandomForestRegressor
# from sentence_transformers import SentenceTransformer

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# AI Models
# encoder = SentenceTransformer("all-MiniLM-L6-v2")
# model = RandomForestRegressor()


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
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = utils.authenticate_employee(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    
    access_token = utils.create_access_token(data={"sub": user.id})
    refresh_token = utils.create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    
@app.post("/set-password/")
async def create_password(form_data: dict):
        
    utils.create_password(form_data)
    return {"message": "Password created successfully"}


@app.get("/get-id/")
async def get_id(token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)
    employee = utils.load_employee(employee_id=payload["sub"])
    return employee


@app.post("/refresh")
async def refresh_token(refresh_token_data: dict):
    refresh_token: str = refresh_token_data.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    payload = utils.decode_jwt(refresh_token)
    employee_id: str = payload["sub"]
    # print("Expiration: ", payload["exp"])

    if employee_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Here you could fetch user data from the database if needed
    new_access_token = utils.create_access_token(data={"sub": employee_id})
    new_refresh_token = utils.create_refresh_token(data={"sub": employee_id})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@app.post("/register")
async def register_employee(employee_data: dict):
    """API endpoint for registering a new employee"""
    try:
        utils.create_employee(employee_data)
        return {"message": "Employee registered successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating employee: {str(e)}"
        )


@app.get("/verify-login/")
async def verify_login(token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)
    return {"message": utils.load_employee(employee_id=payload["sub"])}


@app.post("/projects/create")
def create_new_project(request: dict, token: str = Depends(oauth2_scheme)):
    utils.decode_jwt(token)
    project = utils.create_project(**request)
    return {"message": "Project created successfully", "project_id": project.project_id}


# This is used to display stuff on the dashboard
@app.get("/projects/get-projects")
async def dashboard(token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)

    user = utils.load_employee(employee_id=payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")

    if user.authority_level < 3:
        assigned_projects = utils.load_assigned_projects(user.employee_id)
    else:
        assigned_projects = utils.load_all_projects()

    if assigned_projects is None:
        raise HTTPException(status_code=404, detail="Project Search Failed")

    # Return the projects in a dictionary with a descriptive key
    return {"assigned_projects": assigned_projects}


# This is used to display stuff on the project page
@app.get("/projects/{project_id}/")
async def get_tasks(project_id: str, token: str = Depends(oauth2_scheme)):
    payload = utils.decode_jwt(token)

    project = utils.load_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    employee = utils.load_employee(employee_id=payload["sub"])
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