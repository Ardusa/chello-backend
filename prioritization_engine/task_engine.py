import uuid
import models
from services import get_db, load_task
from fastapi import Depends
from sqlalchemy.orm import Session


def refresh_task_man_hours(
    task_id: uuid.UUID, db: Session = Depends(get_db)
) -> models.Task:
    """
    Given a task ID, refresh the task's human estimated man hours, AI estimated man hours, and actual man hours.
    Will not update the task in the database.
    """
    task = load_task(task_id=task_id, db=db)

    task = refresh_task_human_estimated_man_hours(task)
    task = refresh_task_AI_estimated_man_hours(task)
    task = refresh_task_actual_man_hours(task)

    return task


def refresh_task_human_estimated_man_hours(task: models.Task) -> models.Task:
    """
    Refresh the task_human_estimated_man_hours attribute of the task and all of its subtasks recursively.
    Does not update the database.
    """

    for subtask in task.subtasks:
        if subtask.subtasks:
            subtask = refresh_task_human_estimated_man_hours(subtask)

        task.task_human_estimated_man_hours += subtask.task_human_estimated_man_hours

    return task


def refresh_task_AI_estimated_man_hours(task: models.Task) -> models.Task:
    """
    Refresh the task_AI_estimated_man_hours attribute of the task and all of its subtasks recursively.
    Does not update the database.
    """

    for subtask in task.subtasks:
        if subtask.subtasks:
            subtask = refresh_task_AI_estimated_man_hours(subtask)

        task.task_AI_estimated_man_hours += subtask.task_AI_estimated_man_hours
        task.task_actual_man_hours

    return task


def refresh_task_actual_man_hours(task: models.Task) -> models.Task:
    """
    Refresh the task_actual_man_hours attribute of the task and all of its subtasks recursively.
    Does not update the database.
    """

    for subtask in task.subtasks:
        if subtask.subtasks:
            subtask = refresh_task_actual_man_hours(subtask)

        if not subtask.task_actual_man_hours:
            if subtask.task_started and subtask.task_completed:
                subtask.task_actual_man_hours = (
                    subtask.task_completed - subtask.task_started
                ).total_seconds() / 3600.0
                task.task_actual_man_hours += subtask.task_actual_man_hours
            elif subtask.is_finished:
                raise ValueError(
                    "Task is finished but does not have a start and end time."
                )
        else:
            subtask.task_actual_man_hours = None

    return task


def calculate_task_efficiency(task: models.Task, db: Session) -> float:
    """
    Recursively calculate the efficiency of a task based on its subtasks.
    Human estimated man hours / actual man hours
    """
    if not task.subtasks:
        if task.task_actual_man_hours is None:
            return 0.0
        return task.task_human_estimated_man_hours / task.task_actual_man_hours

    total_efficiency = 0.0
    total_weight = 0.0

    for subtask in task.subtasks:
        subtask_efficiency = calculate_task_efficiency(subtask, db)
        weight = subtask.task_AI_estimated_man_hours
        total_efficiency += subtask_efficiency * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return total_efficiency / total_weight