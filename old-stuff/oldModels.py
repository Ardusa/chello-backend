# from datetime import datetime, timedelta
# from pydantic import BaseModel
# from enum import Enum
# from typing import Optional, List
# from passlib.context import CryptContext # type: ignore
# import numpy as np
# import xgboost as xgb # type: ignore
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sentence_transformers import SentenceTransformer
# # import sqlite3

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Load a pretrained sentence embedding model
# embedder = SentenceTransformer("all-MiniLM-L6-v2")

# class TaskStatus(Enum):
#     """Working status of task."""

#     OPEN = "OPEN"
#     """Task is open and ready to be started."""
#     IN_PROGRESS = "IN_PROGRESS"
#     """Task is currently being worked on."""
#     COMPLETED = "COMPLETED"
#     """Task has been completed."""


# class Employee(BaseModel):
#     """Employee model to store employee details."""

#     id: str
#     """Unique identifier for the employee (username or employee ID)."""
#     full_name: str
#     """Full name of the employee."""
#     email: str
#     """Email address of the employee."""
#     position: Optional[int] = 1
#     """Position of the employee in the organization, 1 for base level, 2 for manager, 3 for admin."""
#     enabled: Optional[bool] = True
#     """Flag to enable or disable the employee account."""
#     efficiency_score: Optional[float] = 1.0  # Default efficiency score of 100%
#     """Efficiency score of the employee (default: 100%)."""
#     password: str = "password"
#     """Password for the employee account."""
    
#     def __init__(self, **data):
#         super().__init__(**data)
#         if not self._is_hashed(self.password):
#             self.password = pwd_context.hash(self.password)

#     def _is_hashed(self, password: str) -> bool:
#         """Check if the password is already hashed."""
#         # This checks if the password has the correct format for a bcrypt hash.
#         return password.startswith("$2b$")

#     def dict(self):
#         return {
#             "id": self.id,
#             "full_name": self.full_name,
#             "email": self.email,
#             "position": self.position,
#             "enabled": self.enabled,
#             "efficiency_score": self.efficiency_score,
#             "password": self.password,
#         }

#     def verify_password(self, password: str) -> bool:
#         """Verify the given password against the stored hashed password."""
#         return pwd_context.verify(password, self.password)


# class Task(BaseModel):
#     """Task model to store task details."""

#     name: str
#     """Name of the task."""
#     description: str
#     """Description of the task."""
#     project_id: str = ""
#     """Name of the project the task belongs to."""
#     dependencies: List[str] = []
#     """List of tasks that this task depends on."""
#     subtasks: List[str] = []
#     """List of tasks that are completed only as part of this task."""
#     status: TaskStatus = TaskStatus.OPEN
#     """Current status of the task."""
#     start_date: Optional[datetime] = None
#     """Date when the task was started."""
#     estimated_hours: Optional[int] = None
#     """User estimated time required to complete the task."""
#     calculated_hours: Optional[timedelta] = None
#     """Calculated estimate of time required to complete the task."""
#     actual_hours: Optional[timedelta] = None
#     """Actual time taken to complete the task."""
#     end_date: Optional[datetime] = None
#     """Date when the task was completed."""
#     employees_assigned: List[Employee] = []
#     """List of employees assigned to the task."""

#     def __init__(self, **data):
#         super().__init__(**data)
#         if self.status is TaskStatus.COMPLETED:
#             self.actual_hours = self.end_date - self.start_date
#         if self.start_date is None:
#             self.start_date = datetime.now()
#         # if self.calculated_hours is None:
#         #     self.calculated_hours = calculate_time_estimate(self).calculated_hours
#         if self.end_date is None:
#             self.end_date = None
            
#     def all_employees_assigned(self) -> List[str]:
#         employees: set[Employee] = set()
#         for (e) in self.employees_assigned:
#             employees.update(e)
#         for task in self.subtasks:
#             employees.update([e.id for e in task.employee_assigned])
#         return [e.id for e in self.employees_assigned]


# class Project(BaseModel):
#     id: str
#     name: str
#     description: str
#     tasks: List[Task] = []
    
#     def get_employees_assigned(self) -> List[str]:
#         employees = set()
#         for task in self.tasks:
#             employees.update([e.id for e in task.employees_assigned])
#         return list(employees)

    
# def extract_features(task: Task) -> np.ndarray:
#     """Converts task details into a feature vector for model training."""
#     text_embedding = embedder.encode(task.name + " " + task.description)
#     avg_efficiency = np.mean([e.efficiency_score for e in task.employees_assigned]) if task.employees_assigned else 1.0
#     num_dependencies = len(task.dependencies)
#     return np.hstack([text_embedding, avg_efficiency, num_dependencies])

# # Simulated historical task data
# historical_tasks = [
#     Task(name="Fix bug in authentication", description="Resolve login failure", estimated_hours=4, actual_hours=timedelta(hours=5), employees_assigned=[Employee(id="E1", full_name="Alice", efficiency_score=0.9)]),
#     Task(name="Implement search feature", description="Build a full-text search API", estimated_hours=10, actual_hours=timedelta(hours=12), employees_assigned=[Employee(id="E2", full_name="Bob", efficiency_score=0.8)]),
# ]

# # Prepare dataset
# X = np.array([extract_features(task) for task in historical_tasks])
# y = np.array([task.actual_hours.total_seconds() / 3600 for task in historical_tasks])  # Convert timedelta to hours

# # Train model
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
# rf_model.fit(X_train, y_train)

# # Predict function
# def predict_task_time(task: Task) -> float:
#     features = extract_features(task).reshape(1, -1)
#     return rf_model.predict(features)[0]

# # Example prediction
# new_task = Task(name="Refactor database schema", description="Optimize tables and indexes", employees_assigned=[Employee(id="E3", full_name="Charlie", efficiency_score=0.85)])
# predicted_time = predict_task_time(new_task)
# print(f"Predicted Completion Time: {predicted_time:.2f} hours")