from main import Task

def calculate_time(task: Task):
    """
    Calculate the time required to complete a task based on the subtasks and their durations.
    """
    
    if task.estimated_hours:
        words = task.description.split()
        task.estimated_hours = len(words) / 10  # Assuming an average of 10 words per hour
        return 
    if task.subtasks:
        return sum(calculate_time(subtask) for subtask in task.subtasks)
    
    return task.calculated_hours