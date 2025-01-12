import smtplib
from email.mime.text import MIMEText
from constants import EMAIL, FILE
import models
import json
from typing import List

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

# ! Task Functions


def load_tasks(project_name: str) -> List[models.Task]:
    try:
        with open(FILE.PROJECTS_DIR / project_name + ".json", "r") as f:
            data = json.load(f).get("tasks", {})
            return {
                task_id: models.Task(**task_data)
                for task_id, task_data in data.items()
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ! Project Functions

def create_project(project_data) -> models.Project:
    project = models.Project(**project_data)
    return project


def load_project(project_id) -> models.Project:
    try:
        with open(f"{FILE.PROJECTS_DIR}{project_id}.json", "r") as f:
            load = json.load(f)
            return create_project(load)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_project(project: models.Project):
    with open(f"{FILE.PROJECTS_DIR}{project}.json", "w") as f:
        json.dump(project.model_dump(), f, indent=4)

        
# ! Linking Functions

def append_task_to_project(project_id: str, task_id: str):
    """Append the given task to the project with the given name."""
    project = load_project(project_id)
    if project is None:
        raise ValueError(f"Project with ID: '{project_id}' does not exist.")
    
    project.tasks.append(task_name)
    models.update_project(project)