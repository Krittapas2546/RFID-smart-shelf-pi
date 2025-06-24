import socket
import json
import time
import random

def send_job_data(host='127.0.0.1', port=8000):
    """ส่งข้อมูล job ไปยัง socket server"""
    
    # สร้างข้อมูล job
    job_data = {
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
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"📡 Connecting to {host}:{port}...")
            client_socket.connect((host, port))
            print("✅ Connected.")

            # Convert dictionary to JSON string and encode to bytes
            message = json.dumps(job_data).encode('utf-8')

            print(f"📤 Sending Job Data:\n{json.dumps(job_data, indent=4)}")
            client_socket.sendall(message)
            
            # รอรับข้อความยืนยัน
            response = client_socket.recv(1024).decode('utf-8')
            print(f"📨 Server response: {response}")
            
            print("✔️ Data sent successfully.")

    except ConnectionRefusedError:
        print(f"❌ Connection refused. Is the server running on {host}:{port}?")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    print("🎯 Job Sender - Testing socket connection")
    print("=" * 50)
    send_job_data()
    print("=" * 50)
    print("✅ Test completed!")
