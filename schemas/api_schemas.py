from typing import List
from pydantic import BaseModel

from schemas import project_model


class MessageResponse(BaseModel):
    message: str


class SetPasswordForm(BaseModel):
    id: str
    temporary_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenForm(BaseModel):
    refresh_token: str


class GetProjectsResponse(BaseModel):
    projects: List[project_model.ProjectResponse]
    
class CreateNewAccountForm(BaseModel):
    """
    Attributes:
        name (str): Name of the user.
        email (str): Email address of the user.
        password (str): Password of the user.
        company_id (str): Name of the company the user belongs to.
        manager_id (str): ID of the manager of the user.
        position (str): Position of the user within the company.
    """
    name: str
    email: str
    password: str
    company_id: str
    manager_id: str
    position: str