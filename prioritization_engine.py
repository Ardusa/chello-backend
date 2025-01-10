from main import Task
from datetime import datetime, timedelta

def calculate_time_estimate(task: Task) -> Task:
    """
    Calculate the time required to complete a task based on the subtasks and their durations.
    """
    if task.estimated_hours:
        task.calculated_hours = task.estimated_hours
        # TODO: Add logic to calculate time based on past data
    elif task.subtasks:
        # Fetch actual Task objects for subtasks and sum their estimates
        task.calculated_hours = sum(calculate_time_estimate(subtask).calculated_hours for subtask in task.subtasks)

    return task  # Allow chaining
def calculate_time_of_completion(task: Task) -> Task:
    """
    Calculate the time of completion of a task based on the start date and the time required to complete the task.
    """
    if task.start_date and task.end_date:
        return task.end_date - task.start_date
    else:
        raise ValueError("Start date or end date is missing")

def calculate_efficiency(task: Task) -> float:
    """Calculate the efficiency of a task based on the estimated time and the actual time taken."""
    task.calculated_hours = calculate_time_estimate(task)
    
    calculate_time_of_completion(task)
    return task. / estimated_time