import asyncio
import json
import logging
import socket
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette import status

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- In-memory Storage ---
class ShelfStateManager:
    """Manages the state of the shelf grid in memory."""
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        # Initialize grid with all cells empty
        self.grid_state = {
            f"{r},{c}": {"status": "empty", "data": None}
            for r in range(1, rows + 1)
            for c in range(1, cols + 1)
        }
        logging.info(f"Shelf state manager initialized for a {rows}x{cols} grid.")

    def update_state(self, location: dict, data: dict):
        """Updates the state of a specific cell."""
        row, col = location.get("row"), location.get("col")
        if not (1 <= row <= self.rows and 1 <= col <= self.cols):
            logging.error(f"Invalid location received: {location}")
            return

        key = f"{row},{col}"
        if data.get("action") == "PUT":
            self.grid_state[key] = {"status": "occupied", "data": data}
            logging.info(f"✅ State for location ({row}, {col}) updated to 'occupied'.")
        elif data.get("action") == "REMOVE":
            self.grid_state[key] = {"status": "empty", "data": None}
            logging.info(f"🗑️ State for location ({row}, {col}) updated to 'empty'.")
        else:
             logging.warning(f"Unknown action '{data.get('action')}' for location ({row}, {col}).")


    def get_all_states(self) -> dict:
        """Returns the entire state of the grid."""
        return self.grid_state

# Initialize the manager for a 5x5 grid
shelf_state_manager = ShelfStateManager(rows=5, cols=5)

# --- Socket Server for RFID Reader ---
async def run_socket_server(host='0.0.0.0', port=65432):
    """Runs a TCP socket server to listen for data from the RFID reader."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.setblocking(False)  # Non-blocking for asyncio
    logging.info(f"✅ Socket Server is listening on {host}:{port}")

    loop = asyncio.get_event_loop()
    while True:
        try:
            conn, addr = await loop.sock_accept(server_socket)
            logging.info(f"🤝 Connection received from {addr}")
            asyncio.create_task(handle_socket_client(conn))
        except Exception as e:
            logging.error(f"Error in socket server: {e}")
            await asyncio.sleep(1) # Prevent busy-looping on error


async def handle_socket_client(conn: socket.socket):
    """Handles a single client connection on the socket server."""
    loop = asyncio.get_event_loop()
    try:
        with conn:
            while True:
                data = await loop.sock_recv(conn, 1024) # 1KB buffer
                if not data:
                    break
                try:
                    payload = json.loads(data.decode('utf-8'))
                    logging.info("📥 Received job data via socket:")
                    logging.info(json.dumps(payload, indent=2))
                    # Update state based on the received data
                    location = payload.get("location")
                    if location:
                        shelf_state_manager.update_state(location, payload)
                    else:
                        logging.warning("Received data with no location info.")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logging.error(f"Failed to decode received data: {e} - Data: {data}")
    except ConnectionResetError:
        logging.warning("Client connection was forcibly closed.")
    except Exception as e:
        logging.error(f"Error handling socket client: {e}")
    finally:
        logging.info("Socket client disconnected.")


# --- FastAPI Application ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the socket server in the background
    asyncio.create_task(run_socket_server())
    yield
    # Clean up resources if needed (not necessary for this example)

app = FastAPI(lifespan=lifespan)

# CORS (Cross-Origin Resource Sharing) Middleware
origins = [
    "http://localhost:3000",  # React default port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/api/shelf-state")
async def get_shelf_state():
    """HTTP endpoint to get the current state of all shelf cells."""
    return shelf_state_manager.get_all_states()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint to stream shelf state updates to the frontend."""
    # For debugging, let's log the origin header
    origin = websocket.headers.get('origin')
    logging.info(f"WebSocket connection attempt from origin: {origin}")

    # --- THIS IS THE CHANGED PART ---
    # We accept the connection first to establish communication.
    await websocket.accept()
    logging.info(f"WebSocket connection accepted from: {websocket.client.host}")
    # --- END OF CHANGE ---

    try:
        # Continuously send the full state to the client
        while True:
            await websocket.send_json(shelf_state_manager.get_all_states())
            # Send updates every 2 seconds
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logging.warning(f"WebSocket client disconnected: {websocket.client.host}")
    except Exception as e:
        logging.error(f"Error in WebSocket communication: {e}")

