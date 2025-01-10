from fastapi import FastAPI, WebSocket
import json

app = FastAPI()

tasks = {
    "Gather Requirements": [],
    "Design Database Schema": ["Gather Requirements"],
    "Develop Backend API": ["Design Database Schema"],
    "Develop Frontend UI": ["Develop Backend API"],
    "Implement Authentication System": ["Develop Backend API"],
    "Write Unit Tests": ["Develop Backend API", "Develop Frontend UI"],
    "Perform Integration Testing": ["Write Unit Tests"],
    "Deploy Application": ["Perform Integration Testing"],
    "Monitor System Performance": ["Deploy Application"],
}

@app.get("/get_dependencies")
async def get_dependencies():
    return tasks

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(json.dumps(tasks))  # Send current dependencies