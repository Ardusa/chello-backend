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
    ACCESS_TOKEN_EXPIRE_MINUTES = 20
    REFRESH_TOKEN_EXPIRE_MINUTES = 60

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

# def load_project_tasks(project_id: str, employee_id: str, tasks: dict, projects: dict) -> List[dict]:
#     """
#     Retrieves all tasks for a project assigned to an employee in hierarchical order.
    
#     Args:
#     - project_id (str): The ID of the project to fetch tasks for.
#     - employee_id (str): The ID of the employee to filter tasks by.
#     - tasks (dict): A dictionary of all tasks indexed by task_id.
#     - projects (dict): A dictionary of all projects indexed by project_id.
    
#     Returns:
#     - list: A list of tasks for the project that the employee is assigned to, in hierarchical order.
#     """
#     # First, get the project and its task IDs
#     project = projects.get(project_id)
#     if not project:
#         return []  # No project found
    
#     task_ids = project.get('tasks', [])
    
#     if not task_ids:
#         return []  # No tasks assigned to this project
    
#     # Load all tasks and filter by employee involvement
#     task_list_with_depth = []
    
#     for task_id in task_ids:
#         # Load task and its sub-tasks
#         task = load_task_with_children(task_id, tasks)
        
#         if not task:
#             continue
        
#         # Filter tasks by employee involvement
#         filtered_task = filter_tasks_by_employee(task, employee_id)
        
#         if filtered_task:
#             # Generate task list with depth for each relevant task
#             task_list_with_depth.extend(generate_task_list_with_depth(filtered_task))
    
#     return task_list_with_depth