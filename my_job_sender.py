import socket
import json
import time

def send_custom_job(lot_no, employee_id, station="Station-A", row=1, col=1):
    """ส่งงานที่กำหนดเองไปยังระบบ"""
    
    job_data = {
        "action": "PUT",
        "status": "Waiting",
        "lotNo": lot_no,
        "from": station,
        "employeeId": employee_id,
        "location": {
            "row": row,
            "col": col
        },
        "timestamp": time.strftime("%H:%M:%S"),
        "error": None
    }
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"🔗 เชื่อมต่อ server...")
            client_socket.connect(('127.0.0.1', 8000))
            
            message = json.dumps(job_data).encode('utf-8')
            client_socket.sendall(message)
            
            response = client_socket.recv(1024).decode('utf-8')
            print(f"✅ ส่งงานสำเร็จ: {lot_no}")
            print(f"📍 ตำแหน่งที่ {row},{col}")
            print(f"👤 พนักงาน: {employee_id}")
            return True
            
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")
        return False

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    print("🎯 ระบบส่งงานแบบกำหนดเอง")
    print("=" * 40)
    
    # ส่งงานแรก
    send_custom_job("LOT-001", "EMP001", "Station-A", 1, 1)
    
    # ส่งงานที่สอง
    send_custom_job("LOT-002", "EMP002", "Station-B", 2, 3)
    
    # ส่งงานที่สาม
    send_custom_job("LOT-003", "EMP003", "Station-C", 4, 6)
    
    print("=" * 40)
    print("✅ ส่งงานเสร็จสิ้น!")
