"""
All Constant Values are defined here
"""

class THRESHOLDS:
    STRONG_THRESHOLD: float= 0.65
    WEAK_THRESHOLD: float= 0.6

class DAG:
    DAG_PATH: str = "Assets/Graphs"
    DAG_EXTENSION: str = ".png"
    DAG_NODE_MULTIPLIER: str = 2.0

class AUTH:
    SECRET_KEY = "CHELLO"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 120

class FILE:
    EMPLOYEES_FILE = "employees.json"
    PROJECTS_DIR = "projects/"
    MODEL_DATA_FILE = "model_data.json"
    TASKS_FILE = "tasks.json"

class HOST:
    LOCAL_HOST = "127.0.0.1"
    LAN_HOST = "192.168.0.80"
    
class EMAIL:
    EMAIL_ADDRESS = "example123@chello.team"
    SIGNATURE = "\n\nThanks for your support!\nChello Team"


# employees: dict[str, models.Employee] = {
#     "ardusa": models.Employee(
#         id="ardusa", full_name="Ankur Desai", email="ardusa05@gmail.com", position=3
#     ),
#     "school": models.Employee(
#         id="school",
#         full_name="Michigan State",
#         email="desaia11@msu.edu",
#         password="chello",
#     ),
# }

# Hello, I was interested in investing into Jira but was curious as to the AI capabilities. What I am looking for is time based prioritization of tasks given team member skills, complexity of task, and hours spent on the project. I am also looking for the calendar to update live to account for longer-than-normal task situations. Please let me know if Jira has these capabilities, and if not, what does it offer that is similar.

# Thank You!