from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio

app = FastAPI()

# Task Model
class Task(BaseModel):
    name: str
    duration_days: int
    dependencies: list[str] = []
    start_date: datetime | None = None
    end_date: datetime | None = None

# In-memory storage (Replace with DB later)
tasks = {}

# Function to schedule tasks
def schedule_tasks():
    scheduled_tasks = {}
    for task_name, task in tasks.items():
        if not task.dependencies:
            start_date = datetime.now()
        else:
            latest_end = max(tasks[dep].end_date for dep in task.dependencies if dep in tasks)
            start_date = latest_end if latest_end else datetime.now()
        
        task.start_date = start_date
        task.end_date = start_date + timedelta(days=task.duration_days)
        scheduled_tasks[task_name] = task
    return scheduled_tasks

# API Endpoint: Add Task
@app.post("/add_task/")
def add_task(task: Task):
    tasks[task.name] = task
    return {"message": "Task added", "task": task}

# API Endpoint: Get Schedule
@app.get("/schedule/")
def get_schedule():
    return schedule_tasks()

# Live Update WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(10)  # Check for overruns every 10s
        for task in tasks.values():
            if task.end_date and task.end_date < datetime.now():
                task.end_date += timedelta(days=1)  # Extend by 1 day for demo
                await websocket.send_json({"task": task.name, "new_end_date": task.end_date.isoformat()})