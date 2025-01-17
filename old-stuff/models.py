import sqlite3
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Database:
    def __init__(self, db_file="chello.db"):
        self.db_file = db_file

    def connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            project_name TEXT NOT NULL,
            description TEXT,
            start_date TEXT,
            end_date TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            task_name TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT,
            parent_task_id TEXT,
            estimated_hours FLOAT,
            actual_hours FLOAT,
            start_date TEXT,
            end_date TEXT,
            project_id TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(project_id),
            FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id)
        );

        CREATE TABLE IF NOT EXISTS task_dependencies (
            task_id TEXT,
            dependent_task_id INTEGER,
            PRIMARY KEY (task_id, dependent_task_id),
            FOREIGN KEY (task_id) REFERENCES tasks(task_id),
            FOREIGN KEY (dependent_task_id) REFERENCES tasks(task_id)
        );

        CREATE TABLE IF NOT EXISTS employee_assignments (
            task_id TEXT,
            employee_id TEXT,
            assigned_date TEXT,
            PRIMARY KEY (task_id, employee_id),
            FOREIGN KEY (task_id) REFERENCES tasks(task_id)
        );

        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            authority_level INTEGER NOT NULL,
            title TEXT NOT NULL
        );
        """)
        conn.commit()
        conn.close()


class Task:
    def __init__(
        self,
        task_id: str,
        description: str,
        project_id: str,
        status: str = "OPEN",
        parent_task_id: Optional[str] = None,
        estimated_hours: Optional[int] = None,
        actual_hours: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        self.task_id = task_id
        self.description = description
        self.project_id = project_id
        self.status = status
        self.parent_task_id = parent_task_id
        self.estimated_hours = estimated_hours
        self.actual_hours = actual_hours
        self.start_date = start_date
        self.end_date = end_date

        if self.status == "COMPLETED":
            self.actual_hours = self.end_date - self.start_date
        if self.start_date is None:
            self.start_date = datetime.now()


    def save(self, db: Database):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO tasks (task_id, task_name, description, status, estimated_hours, actual_hours, 
                        start_date, end_date, project_id, parent_task_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                self.task_id,
                self.task_id,
                self.description,
                self.status,
                self.estimated_hours,
                self.actual_hours,
                self.start_date,
                self.end_date,
                self.project_id,
                self.parent_task_id,
            ),
        )
        conn.commit()
        conn.close()


class Employee:
    def __init__(
        self,
        employee_id: str,
        name: str,
        password: str,
        email: str,
        authority_level: int = 1,
        title: str = "Employee",
    ):
        self.employee_id = employee_id
        self.name = name
        self.password = password
        self.email = email
        self.authority_level = authority_level  # Integer for authority level (1, 2, 3)
        self.title = (
            title  # String for job title (e.g., "Project Manager", "Software Engineer")
        )
        if not self._is_hashed(self.password):
            self.password = pwd_context.hash(self.password)

    def _is_hashed(self, password: str) -> bool:
        """Check if the password is already hashed."""
        # This checks if the password has the correct format for a bcrypt hash.
        return password.startswith("$2b$")

    def verify_password(self, password: str) -> bool:
        """Verify the given password against the stored hashed password."""
        return pwd_context.verify(password, self.password)

    def save(self, db: Database):
        """Save employee to the database"""
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO employees (employee_id, name, password, email, authority_level, title)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                self.employee_id,
                self.name,
                self.password,
                self.email,
                self.authority_level,
                self.title,
            ),
        )
        conn.commit()
        conn.close()


class Project:
    def __init__(
        self,
        project_id: str,
        project_name: str,
        description: str,
        start_date: str,
        end_date: str,
    ):
        self.project_id = project_id
        self.project_name = project_name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date

    def save(self, db: Database):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO projects (project_id, project_name, description, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
        """,
            (
                self.project_id,
                self.project_name,
                self.description,
                self.start_date,
                self.end_date,
            ),
        )
        conn.commit()
        conn.close()
