import asyncio
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

# --- Models for incoming data ---
class Location(BaseModel):
    row: int
    col: int

class Job(BaseModel):
    lotNo: str
    formTo: str  # Renamed from 'from' to avoid keyword conflict
    employeeId: str
    timestamp: str
    status: str
    location: Optional[Location] = None
    error: bool = False

# --- Basic App Setup ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- In-memory state management ---
# These variables will hold the current state of the application.
# In a real-world scenario, you might use a database or a more robust state management solution.
# --- CHANGED: Updated shelf dimensions to 4x6 ---
SHELF_ROWS = 4
SHELF_COLS = 6
job_queue: List[Job] = []
active_job: Optional[Job] = None
# Initialize an empty shelf state
global_shelf_state = [[False for _ in range(SHELF_COLS)] for _ in range(SHELF_ROWS)]

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- API Endpoint to receive new jobs ---
@app.post("/api/submit_job")
async def submit_job(job: Job):
    """
    This endpoint receives a new job from an external system.
    It updates the application's state and broadcasts the new state to all connected clients.
    """
    global active_job, job_queue, global_shelf_state

    print(f"Received new job: {job.lotNo}")

    # Set the new job as the active job and update the queue
    # For simplicity, we'll only show the latest job in the queue
    active_job = job
    job_queue = [job]

    # Update the shelf state based on the new job's location
    # 1. Reset the entire shelf state
    global_shelf_state = [[False for _ in range(SHELF_COLS)] for _ in range(SHELF_ROWS)]
    # 2. If the new job has a location, mark it as active
    if job.location:
        if 0 <= job.location.row < SHELF_ROWS and 0 <= job.location.col < SHELF_COLS:
            global_shelf_state[job.location.row][job.location.col] = True
        else:
            print(f"Warning: Job location {job.location} is out of bounds for the shelf.")


    # Prepare the data packet to be sent to the UI
    update_data = {
        "type": "job_update",
        "job": active_job.model_dump(),  # Use .model_dump() for Pydantic v2+
        "shelf_state": global_shelf_state,
    }

    # Broadcast the update to all connected WebSocket clients
    await manager.broadcast(json.dumps(update_data))

    return {"status": "success", "message": f"Job {job.lotNo} received and broadcasted."}


# --- WebSocket Endpoint for real-time UI updates ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # When a client first connects, send them the current state
        # This ensures the UI is populated immediately without waiting for a new job
        if active_job:
            initial_data = {
                "type": "job_update",
                "job": active_job.model_dump(),
                "shelf_state": global_shelf_state,
            }
            await websocket.send_text(json.dumps(initial_data))

        # Keep the connection alive to receive further updates
        while True:
            # We are just keeping the connection open.
            # The server will proactively push updates via manager.broadcast()
            # The client doesn't need to send any messages.
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"An error occurred in the WebSocket connection: {e}")
        manager.disconnect(websocket)


# --- Frontend Endpoint to serve the HTML page ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("shelf_ui.html", {"request": request})