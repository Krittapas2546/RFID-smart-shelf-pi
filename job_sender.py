import socket
import json
import time
import random

pi_host_ip = '127.0.0.1'  # เปลี่ยนเป็น IP ของ Raspberry Pi ที่ต้องการเชื่อมต่อ

def send_job_to_pi(job_data, host=pi_host_ip, port=65432):  # เปลี่ยนจาก 8000 เป็น 65432
    """
    Connects to the Raspberry Pi server and sends job data.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"📡 Connecting to {host}:{port}...")
            client_socket.connect((host, port))
            print("✅ Connected.")

            # Convert dictionary to JSON string and encode to bytes
            message = json.dumps(job_data).encode('utf-8')

            print(f"📤 Sending Job Data:\n{json.dumps(job_data, indent=4)}")
            client_socket.sendall(message)
            print("✔️ Data sent successfully.")

    except ConnectionRefusedError:
        print(f"❌ Connection refused. Is the server script running on {host}?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    job_to_send = {
        "action": "PUT",
        "status": "Waiting",
        "lotNo": f"LOT-{random.randint(1000, 9999)}",
        "from": "Station-A",
        "employeeId": "2025014",
        "location": {
            "row": random.randint(1, 4),
            "col": random.randint(1, 6)
        },
        "timestamp": time.strftime("%H:%M:%S"),
        "error": None
    }

    print("🎯 Job Sender - Sending job to server")
    print("=" * 50)
    send_job_to_pi(job_to_send, host=pi_host_ip)
    print("=" * 50)
    print("✅ Job sending completed!")
