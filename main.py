# from detect_dependencies import detect_dependencies
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from generate_DAG import generate_DAG
import json
import base64
import uvicorn

app = FastAPI()

# Store tasks and dependencies (Initially empty, will be updated dynamically)
tasks = {}
dependencies = {}

@app.post("/set_tasks")
async def set_tasks(new_tasks: dict):
    global tasks, dependencies
    tasks = new_tasks
    # dependencies = detect_dependencies(tasks)
    # generate_DAG(dependencies, title="DAG_Visualization")  # Generate the DAG PNG
    return {"tasks": tasks, "dependencies": dependencies}

@app.post("/set_dependencies")
async def set_dependencies(new_dependencies: dict):
    global dependencies
    dependencies = new_dependencies  # Update dependencies
    return {"dependencies": dependencies}

@app.get("/get_dependencies")
async def get_dependencies():
    return {"dependencies": dependencies}

@app.get("/generate_test_data")
async def generate_test_data():
    global tasks, dependencies
    
    test_tasks = {
        "Gather Requirements": "Identify and document all functional and non-functional requirements before starting development.",
        "Design Database Schema": "Define tables, relationships, and constraints before implementing the backend.",
        "Develop Backend API": "Implement the server-side logic and endpoints after designing the database schema.",
        "Develop Frontend UI": "Create user interface components after the backend API is functional.",
        "Implement Authentication System": "Integrate user authentication after backend development is completed.",
        "Write Unit Tests": "Develop unit tests for core modules after backend and frontend development.",
        "Perform Integration Testing": "Test interactions between frontend and backend after unit testing is completed.",
        "Deploy Application": "Deploy the application after passing integration tests.",
        "Monitor System Performance": "Continuously monitor application performance after deployment.",
    }

    test_dependencies = {
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
    
    # set_tasks(new_tasks=test_tasks)
    # set_dependencies(new_dependencies=test_dependencies)
    
    tasks = test_tasks
    dependencies = test_dependencies
    generate_DAG(dependencies=dependencies, title="DAG_Visualization")

    return {"tasks": tasks, "dependencies": dependencies, "image" : encode_image()}
    # return {"tasks": test_tasks, "dependencies": test_dependencies}

def encode_image():
    """ Reads the DAG PNG file and converts it to a Base64 string """
    with open("Assets/Graphs/DAG_Visualization.png", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Connected to Client")
    try:
        while True:
            image_base64 = encode_image()  # Convert PNG to Base64
            data = {
                "dependencies": dependencies,
                "image": image_base64  # Send image as Base64 string
            }
            await websocket.send_text(json.dumps(data))  # Send dependencies & image
    except WebSocketDisconnect:
        print("WebSocket disconnected")

# Run server only if this script is the main entry point
if __name__ == "__main__":
    local_host = "127.0.0.1"
    LAN_host = "192.168.0.80"
    uvicorn.run("main:app", host=LAN_host, port=8000, reload=True)