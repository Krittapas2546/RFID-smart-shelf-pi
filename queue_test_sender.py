import socket
import json
import time

class QueueTestSender:
    def __init__(self, host='127.0.0.1', port=8001):
        self.host = host
        self.port = port
    
    def send_job_action(self, action, lot_no, employee_id, row, col, station="Station-A"):
        """ส่งคำสั่ง PUT/GET ไปยังระบบ"""
        
        job_data = {
            "action": action,
            "status": "Waiting" if action == "PUT" else "Processing",
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
                client_socket.connect((self.host, self.port))
                
                message = json.dumps(job_data).encode('utf-8')
                client_socket.sendall(message)
                
                response = client_socket.recv(1024).decode('utf-8')
                
                action_text = "PUT" if action == "PUT" else "GET"
                print(f"📤 {action_text} {lot_no} at ({row},{col})")
                print(f"📨 Response: {response}")
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def test_single_queue():
    """ทดสอบ: คิวเดียว - ควรเลือกอัตโนมัติ"""
    print("🎯 ทดสอบ: คิวเดียว (เลือกอัตโนมัติ)")
    print("=" * 40)
    
    sender = QueueTestSender()
    
    # ส่งงานเดียว
    print("1️⃣ ส่งงาน LOT-001")
    sender.send_job_action("PUT", "LOT-001", "EMP001", 1, 1)
    
    print("✅ ควรเห็นงานแสดงอัตโนมัติ (ไม่ต้องเลือก)")
    print()

def test_multiple_queue():
    """ทดสอบ: หลายคิว - ควรให้เลือก"""
    print("📋 ทดสอบ: หลายคิว (ต้องเลือก)")
    print("=" * 40)
    
    sender = QueueTestSender()
    
    # ส่งหลายงาน
    print("1️⃣ ส่งงาน LOT-002")
    sender.send_job_action("PUT", "LOT-002", "EMP002", 1, 2)
    time.sleep(1)
    
    print("2️⃣ ส่งงาน LOT-003")
    sender.send_job_action("PUT", "LOT-003", "EMP003", 1, 3)
    time.sleep(1)
    
    print("3️⃣ ส่งงาน LOT-004")
    sender.send_job_action("PUT", "LOT-004", "EMP004", 1, 4)
    
    print("✅ ควรเห็นคิว 3 งาน ให้เลือกเอง")
    print()

def test_correct_completion():
    """ทดสอบ: ทำถูก - ควรออกจากคิว"""
    print("✅ ทดสอบ: ทำถูก (ออกจากคิว)")
    print("=" * 40)
    
    sender = QueueTestSender()
    
    # PUT และ GET ถูกต้อง
    print("1️⃣ PUT LOT-005 ที่ (2,1)")
    sender.send_job_action("PUT", "LOT-005", "EMP005", 2, 1)
    time.sleep(2)
    
    print("2️⃣ GET LOT-005 จาก (2,1) [ถูก]")
    sender.send_job_action("GET", "LOT-005", "EMP005", 2, 1)
    
    print("✅ ควรเห็น LOT-005 หายไปจากคิว")
    print()

def test_error_stays_in_queue():
    """ทดสอบ: ทำผิด - ควรค้างในคิว"""
    print("❌ ทดสอบ: ทำผิด (ค้างในคิว)")
    print("=" * 40)
    
    sender = QueueTestSender()
    
    # PUT และ GET ผิดตำแหน่ง
    print("1️⃣ PUT LOT-006 ที่ (2,2)")
    sender.send_job_action("PUT", "LOT-006", "EMP006", 2, 2)
    time.sleep(2)
    
    print("2️⃣ GET LOT-006 จาก (3,3) [ผิด!]")
    sender.send_job_action("GET", "LOT-006", "EMP006", 3, 3)
    
    print("❌ ควรเห็น LOT-006 ยังอยู่ในคิว พร้อม Error")
    print()

def test_mix_scenario():
    """ทดสอบ: สถานการณ์ผสม"""
    print("🎭 ทดสอบ: สถานการณ์ผสม")
    print("=" * 40)
    
    sender = QueueTestSender()
    
    # ส่งงานหลายอัน
    print("1️⃣ PUT LOT-007 ที่ (1,5)")
    sender.send_job_action("PUT", "LOT-007", "EMP007", 1, 5)
    time.sleep(1)
    
    print("2️⃣ PUT LOT-008 ที่ (1,6)")
    sender.send_job_action("PUT", "LOT-008", "EMP008", 1, 6)
    time.sleep(1)
    
    print("3️⃣ GET LOT-007 จาก (1,5) [ถูก] - ควรออกจากคิว")
    sender.send_job_action("GET", "LOT-007", "EMP007", 1, 5)
    time.sleep(1)
    
    print("4️⃣ GET LOT-008 จาก (2,6) [ผิด!] - ควรค้างในคิว")
    sender.send_job_action("GET", "LOT-008", "EMP008", 2, 6)
    
    print("🎯 ผลลัพธ์: ควรเหลือแค่ LOT-008 ในคิว (มี Error)")
    print()

def clear_all_jobs():
    """ล้างงานทั้งหมด (สำหรับรีเซ็ต)"""
    print("🧹 ล้างงานทั้งหมด")
    print("=" * 20)
    
    sender = QueueTestSender()
    
    # ส่งคำสั่ง GET สำหรับ lot ที่อาจยังค้างอยู่
    test_lots = ["LOT-001", "LOT-002", "LOT-003", "LOT-004", "LOT-006", "LOT-008"]
    
    for lot in test_lots:
        try:
            # พยายาม GET จากตำแหน่งต่าง ๆ
            for row in range(1, 5):
                for col in range(1, 7):
                    sender.send_job_action("GET", lot, "ADMIN", row, col)
                    time.sleep(0.1)
        except:
            pass
    
    print("✅ พยายามล้างแล้ว")

def main_menu():
    print("🎯 ระบบทดสอบการจัดการคิว")
    print("=" * 45)
    print("เลือกสถานการณ์ที่ต้องการทดสอบ:")
    print("1. 🎯 คิวเดียว (เลือกอัตโนมัติ)")
    print("2. 📋 หลายคิว (ให้เลือก)")  
    print("3. ✅ ทำถูก (ออกจากคิว)")
    print("4. ❌ ทำผิด (ค้างในคิว)")
    print("5. 🎭 สถานการณ์ผสม")
    print("6. 🧹 ล้างงานทั้งหมด")
    print("=" * 45)
    
    choice = input("เลือก (1-6): ")
    
    if choice == "1":
        test_single_queue()
    elif choice == "2":
        test_multiple_queue()
    elif choice == "3":
        test_correct_completion()
    elif choice == "4":
        test_error_stays_in_queue()
    elif choice == "5":
        test_mix_scenario()
    elif choice == "6":
        clear_all_jobs()
    else:
        print("❌ เลือกไม่ถูกต้อง")

if __name__ == "__main__":
    main_menu()
    print("\n" + "=" * 45)
    print("✅ ทดสอบเสร็จสิ้น!")
    print("💡 ดูผลลัพธ์ที่หน้า UI: http://localhost:8001")
