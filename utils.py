from models import Database, Task, Project, Employee, pwd_context
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from email.mime.text import MIMEText
from constants import EMAIL, AUTH
from jose import JWTError, jwt  # type: ignore
from fastapi import HTTPException
import smtplib

db = Database()
db.create_tables()

print("Database connected")


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


def append_task(task: Task, project_id: str, parent_task_id: Optional[str] = None):
    task.project_id = project_id  # Associate task with a project
    task.parent_task_id = parent_task_id  # Associate with a parent task if provided
    task.save(db)  # Save task to the database


def add_task_dependency(task_id: str, dependent_task_id: str):
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO task_dependencies (task_id, dependent_task_id)
    VALUES (?, ?)
    """,
        (task_id, dependent_task_id),
    )
    conn.commit()
    conn.close()


def load_tasks(project_id: str) -> List[Task]:
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE project_id=?", (project_id,))
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        task = Task(
            task_id=row[1],
            description=row[2],
            status=row[3],
            estimated_hours=row[4],
            actual_hours=row[5],
            start_date=row[6],
            end_date=row[7],
            project_id=row[8],
            parent_task_id=row[9],
        )  # Load parent task ID
        tasks.append(task)
    conn.close()
    return tasks


def load_task_dependencies(task_id: str) -> List[Task]:
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT t.task_id, t.description, t.status, t.estimated_hours, t.actual_hours,
           t.start_date, t.end_date, t.project_id
    FROM task_dependencies td
    JOIN tasks t ON td.dependent_task_id = t.task_id
    WHERE td.task_id = ?
    """,
        (task_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        task = Task(
            task_id=row[0],
            description=row[1],
            status=row[2],
            estimated_hours=row[3],
            actual_hours=row[4],
            start_date=row[5],
            end_date=row[6],
            project_id=row[7],
        )
        tasks.append(task)
    return tasks


def load_task_with_children(task_id: str, tasks: dict) -> dict:
    """
    Loads a task along with its child tasks recursively.
    Args:
    - task_id (str): The ID of the task to load.
    - tasks (dict): A dictionary of all tasks indexed by task_id.

    Returns:
    - dict: The task object along with its sub-tasks as nested children.
    """
    task = tasks.get(task_id)
    if not task:
        return None

    # Load sub-tasks (children) if they exist
    children = [
        load_task_with_children(child_id, tasks)
        for child_id in task.get("children", [])
    ]
    task["children"] = children  # Assign the children to the task

    return task


def filter_tasks_by_employee(task: dict, employee_id: str) -> dict:
    """
    Filters a task and its sub-tasks to include only those the employee is assigned to.
    Args:
    - task (dict): The task object to filter.
    - employee_id (str): The ID of the employee to filter by.

    Returns:
    - dict: The task object and its relevant children that the employee is assigned to.
    """
    # Check if the employee is assigned to this task
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT employee_id FROM employee_assignments WHERE task_id=?
        """,
        (task["task_id"],),
    )
    assigned_employee = cursor.fetchone()
    conn.close()

    if not assigned_employee or assigned_employee[0] != employee_id:
        return None  # If the employee is not assigned, return None

    # Filter sub-tasks recursively
    # Load children from the database
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.task_id, t.description, t.status, t.estimated_hours, t.actual_hours,
               t.start_date, t.end_date, t.project_id
        FROM tasks t
        WHERE t.parent_task_id = ?
        """,
        (task["task_id"],),
    )
    rows = cursor.fetchall()
    conn.close()

    children = []
    for row in rows:
        child_task = {
            "task_id": row[0],
            "description": row[1],
            "status": row[2],
            "estimated_hours": row[3],
            "actual_hours": row[4],
            "start_date": row[5],
            "end_date": row[6],
            "project_id": row[7],
        }
        children.append(child_task)

    filtered_children = [
        filter_tasks_by_employee(child, employee_id) for child in children
    ]
    filtered_children = [
        child for child in filtered_children if child is not None
    ]  # Remove None values

    # Assign filtered children back to task
    task["children"] = filtered_children

    return task


def generate_task_list_with_depth(task: dict, depth: int = 0) -> List[dict]:
    """
    Generates a list of tasks with their depth level.
    Args:
    - task (dict): The task to include in the list.
    - depth (int): The current depth level.

    Returns:
    - list: A list of tasks with their depth level.
    """
    task_with_depth = {"task": task, "depth": depth}
    task_list = [task_with_depth]

    # Add child tasks with incremented depth
    for child in task["children"]:
        task_list.extend(generate_task_list_with_depth(child, depth + 1))

    return task_list


def load_and_filter_tasks_for_employee(
    task_id: str, employee_id: str, tasks: dict
) -> List[dict]:
    """
    Loads a task and its relevant sub-tasks for an employee, filtering out tasks the employee is not assigned to,
    and then generates a list with depth information.
    Args:
    - task_id (str): The ID of the task to start from.
    - employee_id (str): The ID of the employee.
    - tasks (dict): A dictionary of all tasks indexed by task_id.

    Returns:
    - list: A list of filtered tasks with depth information.
    """
    # Load the task and its children
    task = load_task_with_children(task_id, tasks)

    if not task:
        return []

    # Filter the tasks by employee involvement
    filtered_task = filter_tasks_by_employee(task, employee_id)

    if not filtered_task:
        return []

    # Generate the task list with depth
    task_list_with_depth = generate_task_list_with_depth(filtered_task)

    return task_list_with_depth


def authenticate_employee(employee_id: str, password: str):
    employee = load_employee(employee_id)
    if not employee:
        print("Employee not found: ", employee_id)
        return False

    passGood = employee.verify_password(password=password)
    if not passGood:
        print("Password incorrect: ", password)
        return False

    return employee


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=AUTH.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta  # Use timezone-aware datetime
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, AUTH.SECRET_KEY, algorithm=AUTH.ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=AUTH.REFRESH_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta  # Use timezone-aware datetime
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, AUTH.SECRET_KEY, algorithm=AUTH.ALGORITHM)


def decode_jwt(token: str) -> dict:
    """
    Decode a JWT token and return the payload.

    Args:
    - token (str): The JWT token to decode.

    Returns:
    - dict: The decoded payload.

    Raises:
    - HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# def create_project(project_data) -> Project:
# project = Project(**project_data)
def create_project(
    project_id: str, project_name: str, description: str, start_date: str, end_date: str
) -> Project:
    project = Project(project_id, project_name, description, start_date, end_date)
    project.save(db)
    return project


def load_project(project_id: str) -> Project:
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE project_id=?", (project_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        project = Project(
            project_id=row[1], description=row[2], start_date=row[3], end_date=row[4]
        )
        return project
    else:
        return None


def load_project_tasks(project_id: str, employee_id: Optional[str]):
    """
    Loads all tasks for a project, including their sub-tasks, in a hierarchical view.
    Optionally filters tasks by employee assignment.
    Args:
    - project_id (str): The project ID to load tasks for.
    - employee_id (Optional[str]): The employee ID to filter tasks by, or None to load all tasks.

    Returns:
    - List[dict]: A list of tasks (and sub-tasks) in hierarchical order.
    """
    # Load tasks for the project
    tasks = load_tasks(project_id)

    # Create a dictionary of tasks by task_id for easy lookup
    task_dict = {task.task_id: task for task in tasks}

    # Load the subtasks for each task
    for task in tasks:
        task.children = [t.task_id for t in tasks if t.parent_task_id == task.task_id]

    # If employee_id is provided, filter the tasks based on their assignments
    if employee_id:
        filtered_tasks = []
        for task in tasks:
            # Only include the task if it's assigned to the employee, or if its subtask is assigned
            task_with_children = filter_tasks_by_employee(task, employee_id)
            if task_with_children:
                filtered_tasks.append(task_with_children)
        return filtered_tasks

    # If no employee_id is provided, return all tasks with their subtasks
    return generate_task_list_with_depth(
        task_dict
        # task_dict[task.task_id]
    )  # Recursive depth generation


def load_assigned_projects(employee_id: str) -> List[Project]:
    """
    Load all projects assigned to a given employee, without creating new tables.

    Args:
    - employee_id (str): The ID of the employee.

    Returns:
    - List[Project]: A list of projects assigned to the employee.
    """
    conn = db.connect()
    cursor = conn.cursor()

    # Get tasks assigned to the employee
    cursor.execute(
        """
    SELECT t.task_id, t.project_id, t.task_name, t.status, t.start_date, t.end_date
    FROM employee_assignments ea
    JOIN tasks t ON ea.task_id = t.task_id
    WHERE ea.employee_id = ?
    """,
        (employee_id,),
    )
    rows = cursor.fetchall()

    # Prepare a list of projects associated with the tasks
    project_ids = set()  # to avoid duplicate project entries

    for row in rows:
        task_id = row[0]
        project_id = row[1]
        task_name = row[2]
        status = row[3]
        start_date = row[4]
        end_date = row[5]

        # Recursively find the project associated with the task
        cursor.execute(
            """
        SELECT p.project_id, p.project_name, p.description, p.start_date, p.end_date
        FROM projects p
        WHERE p.project_id = ?
        """,
            (project_id,),
        )
        project_row = cursor.fetchone()

        if project_row:
            project = Project(
                project_id=project_row[0],
                project_name=project_row[1],
                description=project_row[2],
                start_date=project_row[3],
                end_date=project_row[4],
            )
            project_ids.add(project)  # add project if it's not already in the list

    conn.close()

    return list(project_ids)


def load_all_projects() -> List[Project]:
    """
    Load all projects from the database.

    Returns:
    - List[Project]: A list of all projects.
    """
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    conn.close()

    projects = []
    for row in rows:
        project = Project(
            project_id=row[0],
            project_name=row[1],
            description=row[2],
            start_date=row[3],
            end_date=row[4],
        )
        projects.append(project)

    return projects


def create_employee(
    employee_id: str, name, password: str, email: str, authority_level: int, title: str
):
    existing_employee = load_employee(employee_id)
    if existing_employee:
        raise ValueError(f"An employee with ID: {employee_id} already exists.")

    employee = Employee(employee_id, name, password, email, authority_level, title)
    # def create_employee(data):
    #     employee = Employee(**data)
    # print(name + " password: " + password)
    employee.save(db)
    return employee


def load_employee(employee_id: str):
    """Load an employee by ID"""
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE employee_id=?", (employee_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        employee = Employee(
            employee_id=row[0],
            name=row[1],
            password=row[2],
            email=row[3],
            authority_level=row[4],
            title=row[5],
        )
        return employee
    else:
        return None


def assign_employee_to_task(task_id: str, employee_id: str):
    """Assign an employee to a task"""
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO employee_assignments (task_id, employee_id, assigned_date)
    VALUES (?, ?, ?)
    """,
        (task_id, employee_id, display_current_day_time()),
    )
    conn.commit()
    conn.close()


def get_employees_assigned_to_task(task_id: int) -> List[Employee]:
    """Retrieve all employees assigned to a task"""
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT e.employee_id, e.name, e.authority_level, e.title
    FROM employee_assignments ea
    JOIN employees e ON ea.employee_id = e.employee_id
    WHERE ea.task_id = ?
    """,
        (task_id,),
    )
    employees = cursor.fetchall()
    conn.close()

    return [
        Employee(
            employee_id=row[0],
            name=row[1],
            password=row[2],
            email=row[3],
            authority_level=row[4],
            title=row[5],
        )
        for row in employees
    ]


def display_current_day_time() -> str:
    now = datetime.now()
    day_of_week = now.strftime("%A")  # Full weekday name
    hour = now.strftime("%H")  # Hour (24-hour clock)
    minute = now.strftime("%M")  # Minute
    second = now.strftime("%S")  # Second
    return f"{day_of_week}, {hour}:{minute}:{second}, {now.strftime('%Y-%m-%d')}"


def calculate_work_time(
    start_time: str, end_time: str, weekly_times: dict
) -> timedelta:
    """
    Calculate the total work time between two time periods.

    :param start_time: Start time in the format "{day_of_week}, {hour}:{minute}:{second}, {YYYY-MM-DD}"
    :param end_time: End time in the format "{day_of_week}, {hour}:{minute}:{second}, {YYYY-MM-DD}"
    :param weekly_times: Dictionary with days of the week as keys and a list of tuples (clock_in, clock_out) as values
    :return: Total work time as a timedelta object
    """
    # Define the format string
    time_format = "%A, %H:%M:%S, %Y-%m-%d"

    # Parse the start and end times
    start_dt = datetime.strptime(start_time, time_format)
    end_dt = datetime.strptime(end_time, time_format)

    total_work_time = timedelta()

    current_dt = start_dt
    while current_dt <= end_dt:
        day_of_week = current_dt.strftime("%A")
        if day_of_week in weekly_times:
            for clock_in, clock_out in weekly_times[day_of_week]:
                clock_in_dt = datetime.strptime(clock_in, "%H:%M:%S").replace(
                    year=current_dt.year, month=current_dt.month, day=current_dt.day
                )
                clock_out_dt = datetime.strptime(clock_out, "%H:%M:%S").replace(
                    year=current_dt.year, month=current_dt.month, day=current_dt.day
                )

                if clock_in_dt < start_dt:
                    clock_in_dt = start_dt
                if clock_out_dt > end_dt:
                    clock_out_dt = end_dt

                if clock_in_dt < clock_out_dt:
                    total_work_time += clock_out_dt - clock_in_dt

        current_dt += timedelta(days=1)

    return total_work_time
