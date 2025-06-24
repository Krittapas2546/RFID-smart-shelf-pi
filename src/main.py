import os
import asyncio
import json
import logging
from multiprocessing import Process, Queue
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Get the absolute path of the directory where the current script is located (src)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# --- Path Resolution ---
# Standard path for templates (e.g., src/templates)
templates_path_in_src = os.path.join(BASE_DIR, "templates")
# Alternative path for templates (e.g., <project_root>/templates)
templates_path_in_root = os.path.join(PROJECT_ROOT, "templates")

TEMPLATES_DIR = None
if os.path.isdir(templates_path_in_src):
    TEMPLATES_DIR = templates_path_in_src
elif os.path.isdir(templates_path_in_root):
    TEMPLATES_DIR = templates_path_in_root
else:
    raise RuntimeError(
        "Templates directory not found. Please ensure it exists at "
        f"'{templates_path_in_src}' or '{templates_path_in_root}'"
    )

# Static files directory (e.g., src/static)
STATIC_DIR = os.path.join(BASE_DIR, "static")


# --- FastAPI App Initialization ---
app = FastAPI()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Mount static files
if not os.path.isdir(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
    print(f"Created static directory at: {STATIC_DIR}")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- WebSocket Management ---
active_connections: list[WebSocket] = []
shelf_data_queue = Queue()


# --- Job Queue Management ---
job_queue = []  # เก็บรายการ Lot jobs

def add_job_to_queue(lot_id: str, emp_id: str):
    """เพิ่ม job ใหม่เข้า queue"""
    job = {
        "lot_id": lot_id,
        "emp_id": emp_id,
        "status": "pending",
        "created_at": asyncio.get_event_loop().time()
    }
    job_queue.append(job)
    logging.info(f"➕ Added new job to queue: Lot {lot_id}, Employee {emp_id}")
    return job

def get_job_queue():
    """ดึงรายการ jobs ทั้งหมด"""
    logging.info(f"📋 Retrieved job queue with {len(job_queue)} jobs")
    return job_queue

def select_job(lot_id: str):
    """เลือก job จาก queue"""
    for job in job_queue:
        if job["lot_id"] == lot_id and job["status"] == "pending":
            job["status"] = "selected"
            logging.info(f"✅ Selected job: Lot {lot_id}")
            return job
    logging.warning(f"⚠️ Job not found or already selected: Lot {lot_id}")
    return None


# --- Background RFID Reader Process ---
def start_rfid_reader_process(queue: Queue):
    """
    Initializes and runs the RFID reader in a separate process.
    (This is a placeholder for the actual RFID reader logic)
    """
    print("RFID Reader process started.")
    import time
    import random

    while True:
        # Simulate reading a tag
        tag_id = f"TAG{random.randint(100, 999)}"
        # Simulate an action
        action = random.choice(["added", "removed"])
        data = {"tag_id": tag_id, "action": action}
        print(f"Reader simulated data: {data}")
        queue.put(json.dumps(data))
        time.sleep(5)  # Simulate delay


# --- Application Event Handlers ---
@app.on_event("startup")
async def startup_event():
    """
    Starts the background process for the RFID reader when the app starts.
    """
    print("Application startup...")
    # Start the RFID reader in a separate process
    rfid_process = Process(target=start_rfid_reader_process, args=(shelf_data_queue,))
    rfid_process.daemon = True
    rfid_process.start()
    print("RFID reader process initiated.")


# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for real-time updates.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logging.info(f"🔌 WebSocket connection established. Total clients: {len(active_connections)}")

    try:
        # Send data from the queue to the client
        while True:
            if not shelf_data_queue.empty():
                data = shelf_data_queue.get()
                logging.info(f"📤 Sending data to client: {data}")
                await websocket.send_text(data)
            await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logging.warning(f"🔌 WebSocket connection closed. Total clients: {len(active_connections)}")
    except Exception as e:
        logging.error(f"❌ An error occurred in WebSocket: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main shelf UI page."""
    logging.info("🏠 Serving main shelf UI page")
    return templates.TemplateResponse("shelf_ui.html", {"request": request})


# --- Main Execution ---
if __name__ == "__main__":
    # To run for development:
    # uvicorn src.main:app --reload
    # This command should be run from the project's root directory (RFID-smart-shelf-pi).
    uvicorn.run(app, host="0.0.0.0", port=8000)