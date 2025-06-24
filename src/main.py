import os
import asyncio
import json
import logging
import time
from multiprocessing import Process, Queue
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import socket
import threading

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


# --- Socket Server for External Job Data ---
def handle_job_client(conn, addr):
    """จัดการ client ที่ส่งข้อมูล job มา"""
    logging.info(f"🤝 Job client connected from {addr}")
    try:
        with conn:
            # รับข้อมูลทั้งหมดในครั้งเดียว
            data = conn.recv(4096)  # เพิ่มขนาด buffer
            if not data:
                logging.warning("No data received")
                return
            
            try:
                # แปลง JSON data ที่ได้รับ
                job_data = json.loads(data.decode('utf-8'))
                logging.info(f"📥 Received job data:")
                logging.info(json.dumps(job_data, indent=2))
                
                # ตรวจสอบและประมวลผล PUT/GET actions
                processed_job = process_job_action(job_data)
                
                # ส่งข้อมูลที่ประมวลผลแล้วเข้า queue
                shelf_data_queue.put(json.dumps(processed_job))
                logging.info(f"✅ Job data processed and added to queue")
                
                # ส่งข้อความยืนยันกลับไป
                action_text = "วางชิ้นงาน" if job_data.get('action') == 'PUT' else "เอาชิ้นงานออก"
                status_text = "✅ สำเร็จ" if not processed_job.get('error') else "❌ ผิดพลาด"
                confirmation = f"{status_text} {action_text}: {job_data.get('lotNo', 'N/A')}"
                conn.sendall(confirmation.encode('utf-8'))
                
            except json.JSONDecodeError as e:
                logging.error(f"❌ Failed to decode JSON: {e}")
                logging.error(f"Raw data received: {data}")
                error_msg = "Error: Invalid JSON format"
                conn.sendall(error_msg.encode('utf-8'))
            except Exception as e:
                logging.error(f"❌ Error processing job data: {e}")
                
    except Exception as e:
        logging.error(f"❌ Job client error: {e}")
    finally:
        logging.info(f"🔌 Job client {addr} disconnected")

def start_job_socket_server(host='0.0.0.0', port=8000):
    """เริ่ม socket server สำหรับรับข้อมูล job จากภายนอก"""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))  # ใช้ port 9000
        server_socket.listen(5)
        logging.info(f"🚀 Job Socket server listening on {host}:{port}")
        
        while True:
            conn, addr = server_socket.accept()
            # ใช้ thread ใหม่สำหรับแต่ละ client
            client_thread = threading.Thread(target=handle_job_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        logging.error(f"❌ Job socket server error: {e}")


# --- Background RFID Reader Process ---


# --- Background RFID Reader Process ---
# def start_rfid_reader_process(queue: Queue):
#     """
#     Initializes and runs the RFID reader in a separate process.
#     (This is a placeholder for the actual RFID reader logic)
#     """
#     print("RFID Reader process started.")
#     import time
#     import random

#     while True:
#         # Simulate reading a tag
#         tag_id = f"TAG{random.randint(100, 999)}"
#         # Simulate an action
#         action = random.choice(["added", "removed"])
#         data = {"tag_id": tag_id, "action": action}
#         print(f"Reader simulated data: {data}")
#         queue.put(json.dumps(data))
#         time.sleep(5)  # Simulate delay


# --- Application Event Handlers ---
@app.on_event("startup")
async def startup_event():
    """
    Starts the background process for the RFID reader when the app starts.    """
    print("Application startup...")
    
    # Start the job socket server in a separate thread (only once)
    socket_thread = threading.Thread(target=start_job_socket_server, args=('0.0.0.0', 8000))
    socket_thread.daemon = True
    socket_thread.start()
    logging.info("🚀 Job socket server started on port 8000")
    
    # Start the RFID reader in a separate process
    # rfid_process = Process(target=start_rfid_reader_process, args=(shelf_data_queue,))
    # rfid_process.daemon = True
    # rfid_process.start()
    print("RFID reader process disabled - ready for external job data.")


# --- Job Tracking System ---
# เก็บสถานะชิ้นงานในระบบ
active_jobs = {}  # {"LOT-001": {"location": (1,1), "employee": "EMP001", "timestamp": "..."}}

def process_job_action(job_data):
    """ประมวลผล PUT/GET actions และตรวจสอบความถูกต้อง"""
    action = job_data.get('action', '')
    lot_no = job_data.get('lotNo', '')
    employee_id = job_data.get('employeeId', '')
    location = job_data.get('location', {})
    current_row = location.get('row', 0)
    current_col = location.get('col', 0)
    
    # สร้างสำเนาของ job_data เพื่อแก้ไข
    processed_job = job_data.copy()
    
    if action == 'PUT':
        # การวางชิ้นงาน
        if lot_no in active_jobs:
            # ชิ้นงานมีอยู่แล้ว - ผิดพลาด            processed_job['error'] = f"❌ Lot {lot_no} already exists in system"
            processed_job['status'] = 'Error'
            logging.warning(f"PUT Error: {lot_no} already exists")
        else:
            # วางชิ้นงานใหม่ - สำเร็จ
            active_jobs[lot_no] = {
                'location': (current_row, current_col),
                'employee': employee_id,
                'timestamp': job_data.get('timestamp', ''),
                'from': job_data.get('from', '')
            }
            processed_job['error'] = None
            processed_job['status'] = 'Waiting'
            logging.info(f"PUT Success: {lot_no} placed at ({current_row},{current_col})")
    
    elif action == 'GET':
        # การเอาชิ้นงานออก
        if lot_no not in active_jobs:
            # ไม่มีชิ้นงานในระบบ - ผิดพลาด
            processed_job['error'] = f"❌ Lot {lot_no} not found in system"
            processed_job['status'] = 'Error'
            logging.warning(f"GET Error: {lot_no} not found")
        else:
            stored_job = active_jobs[lot_no]
            stored_location = stored_job['location']
            
            # ตรวจสอบตำแหน่งเท่านั้น
            if (current_row, current_col) != stored_location:
                processed_job['error'] = f"❌ Wrong position! Expected {stored_location}, got ({current_row},{current_col})"
                processed_job['status'] = 'Error'
                logging.warning(f"GET Error: {lot_no} wrong position - expected {stored_location}, got ({current_row},{current_col})")
            else:
                # ตำแหน่งถูกต้อง - เอาออกจากระบบ
                del active_jobs[lot_no]
                processed_job['error'] = None
                processed_job['status'] = 'Completed'
                logging.info(f"GET Success: {lot_no} removed from ({current_row},{current_col})")
    
    else:
        # Action ที่ไม่รู้จัก
        processed_job['error'] = f"❌ Unknown action: {action}"
        processed_job['status'] = 'Error'
        logging.warning(f"Unknown action: {action}")
    
    return processed_job


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
        if websocket in active_connections:            active_connections.remove(websocket)


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
    uvicorn.run(app, host="0.0.0.0", port=8001)