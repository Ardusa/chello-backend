import asyncio
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
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from schemas import account_model, api_schemas, project_model, task_model, company_model

from services import (
    load_task,
    create_task,
    load_project_tasks,
    delete_task,
    load_company,
    load_project,
    create_project,
    load_projects,
    delete_project,
    create_access_token,
    create_refresh_token,
    decode_jwt,
    get_db,
    fetch_table_data,
    save_table_to_file,
    convert_uuid_keys_to_str,
    load_account,
    create_account,
    authenticate_account,
    load_accounts,
    create_company,
)

from utils import password_utils

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
    tables = [
        "tasks",
        "projects",
        "accounts",
        "companies",
    ]  # Adjust to your table names

    try:
        while True:
            for table in tables:
                # Fetch the table data
                table_data = fetch_table_data(table)
                print("Sending Table Data")
                # Save the table data to a file
                save_table_to_file(table, table_data)

            # Wait for 1 second before updating again
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")


@app.get("/")
async def root():
    return {"message": "API is working"}


# ? Verification Endpoints


@app.post("/login", response_model=api_schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        user = authenticate_account(
            email=form_data.username, password=form_data.password, db=db
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@app.get(
    "/verify-login",
    response_model=account_model.AccountResponse,
)
async def verify_login(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_jwt(token)
        account = load_account(account_id=payload["sub"], db=db)
        account.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(account)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )
    return account


@app.patch("/set-password", response_model=api_schemas.MessageResponse)
async def set_password(
    form_data: api_schemas.SetPasswordForm, db: Session = Depends(get_db)
):
    try:
        user = load_account(account_id=form_data.id, db=db)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Link, Account ID not found",
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


@app.post("/refresh", response_model=api_schemas.TokenResponse)
async def refresh_token(
    refresh_token_data: api_schemas.RefreshTokenForm,
    db: Session = Depends(get_db),
):
    refresh_token = refresh_token_data.refresh_token

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        payload = decode_jwt(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        account = load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    new_access_token = create_access_token(data={"sub": account.id})
    new_refresh_token = create_refresh_token(data={"sub": account.id})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


# ? Account Endpoints


@app.get(
    "/accounts/self",
    response_model=account_model.AccountResponse,
)
async def get_self(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        account = load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@app.put("/accounts/register-account", response_model=account_model.AccountResponse)
async def register_account(
    account_data: account_model.AccountCreate,
    db: Session = Depends(get_db),
):
    """API endpoint for registering a new account"""

    try:
        existing_account = load_account(email=account_data.email, db=db)
    except Exception:
        existing_account = None

    if existing_account:
        print(existing_account)
        raise HTTPException(
            status_code=400, detail="An account already exists with that email"
        )

    try:
        account = create_account(account_data=account_data, db=db)
        print("account created: ", account.__dict__)
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating account: {str(e)}")


@app.put(
    "/accounts/register-company-account", response_model=api_schemas.MessageResponse
)
async def register_employee(
    employee_data: account_model.AccountCreate,
    db: Session = Depends(get_db),
):
    """API endpoint for registering a new employee"""
    try:
        create_account(employee_data=employee_data, db=db)
        return {"message": "Employee registered successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating employee: {str(e)}"
        )


@app.get("/accounts/get-accounts")
async def get_accounts(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    payload = decode_jwt(token)
    try:
        manager = load_account(account_id=payload["sub"], db=db)
        accounts = load_accounts(manager, db=db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error getting accounts: {str(e)}")

    return accounts


@app.get(
    "/accounts/{account_id}",
    response_model=account_model.AccountResponse,
)
async def get_account(
    account_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        account = load_account(account_id_str=account_id, db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="That account was not found")

    return account


@app.patch(
    "/accounts/update-account",
    response_model=account_model.AccountResponse,
)
async def update_account(
    account_data: account_model.AccountUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """API endpoint for updating an existing account"""
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        existing_account = load_account(account_id_str=account_data.id, db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    from uuid import UUID

    update_data = account_data.model_dump(exclude_unset=True, exclude={"manager"})

    update_data["id"] = UUID(update_data["id"])
    if update_data["manager_id"]:
        print("updating manager id")
        update_data["manager_id"] = UUID(update_data["manager_id"])
    if update_data["company_id"]:
        print("updating company id")
        update_data["company_id"] = UUID(update_data["company_id"])

    print(update_data)

    for key, value in update_data.items():
        print("setting: ", key, value)
        setattr(existing_account, key, value)

    db.commit()
    db.refresh(existing_account)
    return existing_account


# ? Project Endpoints


@app.put("/projects/create", response_model=project_model.ProjectResponse)
def create_new_project(
    request: project_model.ProjectCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    project = create_project(project_data=request, db=db)
    return project


@app.patch("/projects/{project_id}/", response_model=project_model.ProjectResponse)
def edit_project(
    request: project_model.ProjectCreate,
    project_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    project = load_project(project_id_str=project_id, db=db)

    update_data = request.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)  # Update only changed fields

    db.commit()
    db.refresh(project)
    return project


@app.get("/projects/{project_id}/")
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        account = load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    project = load_project(project_id_str=project_id, db=db)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    display_tasks = load_project_tasks(
        project_id=project.id, account_id=account.id, db=db
    )

    display_tasks_json = convert_uuid_keys_to_str(display_tasks)

    return {"project": project.__dict__, "tasks": display_tasks_json}


@app.delete("/projects/{project_id}", response_model=api_schemas.MessageResponse)
def delete__project(
    project_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    project = load_project(project_id_str=project_id, db=db)

    delete_project(project_id=project.id, db=db)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"message": "Project deleted successfully"}


@app.get("/projects/get-projects")
async def get_projects(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        account = load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    assigned_projects = load_projects(account_id=account.id, db=db)

    return assigned_projects


# ? Task Endpoints


@app.post("/tasks/create-task", response_model=task_model.TaskResponse)
def create_new_task(
    request: task_model.TaskCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    task = create_task(task=request, db=db)

    return task


@app.delete("/tasks/{task_id}", response_model=api_schemas.MessageResponse)
def delete__task(
    task_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    task = load_task(task_id_str=task_id, db=db)

    delete_task(task_id=task.id, db=db)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}


@app.get("/tasks/{task_id}", response_model=task_model.TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    task = load_task(task_id_str=task_id, db=db)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.patch("/tasks/update-task", response_model=task_model.TaskResponse)
def update_task(
    request: task_model.TaskUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    task = load_task(task_id_str=request.id, db=db)

    from uuid import UUID

    update_data = request.model_dump(exclude_unset=True)
    update_data["id"] = UUID(update_data["id"])
    update_data["project_id"] = UUID(update_data["project_id"])
    update_data["assigned_to"] = UUID(update_data["assigned_to"])
    if update_data.get("parent_task_id"):
        update_data["parent_task_id"] = UUID(update_data["parent_task_id"])

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


# ? Company Endpoints


@app.put("/companies/create")
def create_new_company(
    company_data: company_model.CompanyCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    company = create_company(company_data=company_data, db=db)
    return company


@app.get("/companies/logo")
def get_company_logo(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token is invalid or expired: {str(e)}"
        )

    try:
        account = load_account(account_id=payload["sub"], db=db)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        company = load_company(company_id=account.company_id, db=db)
    except Exception:
        return ""

    return company.logo
