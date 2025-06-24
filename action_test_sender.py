import socket
import json
import time
import random

class JobActionSender:
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
    
    def send_job_action(self, action, lot_no, employee_id, row, col, station="Station-A"):
        """ส่งคำสั่ง PUT/GET ไปยังระบบ"""
        
        job_data = {
            "action": action,  # "PUT" หรือ "GET"
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
                print(f"🔗 เชื่อมต่อ server...")
                client_socket.connect((self.host, self.port))
                
                message = json.dumps(job_data).encode('utf-8')
                client_socket.sendall(message)
                
                response = client_socket.recv(1024).decode('utf-8')
                
                action_text = "วางชิ้นงาน" if action == "PUT" else "เอาชิ้นงานออก"
                print(f"✅ {action_text} สำเร็จ: {lot_no}")
                print(f"📍 ตำแหน่งที่ {row},{col} | 👤 {employee_id}")
                print(f"📨 Server: {response}")
                return True
                
        except Exception as e:
            print(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def put_job(self, lot_no, employee_id, row, col, station="Station-A"):
        """วางชิ้นงาน (PUT)"""
        return self.send_job_action("PUT", lot_no, employee_id, row, col, station)
    
    def get_job(self, lot_no, employee_id, row, col, station="Station-A"):
        """เอาชิ้นงานออก (GET)"""
        return self.send_job_action("GET", lot_no, employee_id, row, col, station)

# =====================================================
# สถานการณ์จำลอง: ทำถูก vs ทำผิด
# =====================================================

def scenario_correct_workflow():
    """สถานการณ์: ทำงานถูกต้อง"""
    print("✅ === สถานการณ์: ทำงานถูกต้อง ===")
    print("-" * 40)
    
    sender = JobActionSender()
    
    # 1. PUT - วางชิ้นงาน
    print("1️⃣ วางชิ้นงาน LOT-001 ที่ตำแหน่ง (1,1)")
    sender.put_job("LOT-001", "EMP001", 1, 1, "Station-A")
    time.sleep(2)
    
    # 2. GET - เอาชิ้นงานออกจากตำแหน่งเดียวกัน (ถูกต้อง)
    print("\n2️⃣ เอาชิ้นงาน LOT-001 ออกจากตำแหน่ง (1,1)")
    sender.get_job("LOT-001", "EMP001", 1, 1, "Station-A")
    
    print("✅ ขั้นตอนเสร็จสมบูรณ์!")

def scenario_wrong_position():
    """สถานการณ์: เอาชิ้นงานผิดตำแหน่ง"""
    print("❌ === สถานการณ์: เอาชิ้นงานผิดตำแหน่ง ===")
    print("-" * 50)
    
    sender = JobActionSender()
    
    # 1. PUT - วางชิ้นงาน
    print("1️⃣ วางชิ้นงาน LOT-002 ที่ตำแหน่ง (2,2)")
    sender.put_job("LOT-002", "EMP002", 2, 2, "Station-B")
    time.sleep(2)
    
    # 2. GET - เอาชิ้นงานออกจากตำแหน่งผิด (ผิด!)
    print("\n2️⃣ เอาชิ้นงาน LOT-002 ออกจากตำแหน่ง (3,3) [ผิด!]")
    sender.get_job("LOT-002", "EMP002", 3, 3, "Station-B")
    
    print("❌ ขั้นตอนผิดพลาด - ตำแหน่งไม่ตรงกัน!")

def scenario_wrong_employee():
    """สถานการณ์: คนอื่นเอาชิ้นงาน (ไม่มีการตรวจสอบแล้ว)"""
    print("ℹ️ === หมายเหตุ: ระบบไม่ตรวจสอบพนักงานแล้ว ===")
    print("-" * 50)
    
    sender = JobActionSender()
    
    # 1. PUT - วางชิ้นงาน
    print("1️⃣ วางชิ้นงาน LOT-003 ที่ตำแหน่ง (1,3) โดย EMP003")
    sender.put_job("LOT-003", "EMP003", 1, 3, "Station-C")
    time.sleep(2)
    
    # 2. GET - คนอื่นเอาชิ้นงาน (จะสำเร็จเพราะไม่ตรวจสอบพนักงาน)
    print("\n2️⃣ EMP999 เอาชิ้นงาน LOT-003 ออกจากตำแหน่ง (1,3) [จะสำเร็จ]")
    sender.get_job("LOT-003", "EMP999", 1, 3, "Station-C")
    
    print("✅ ขั้นตอนสำเร็จ - ระบบไม่ตรวจสอบพนักงาน!")

def scenario_production_line():
    """สถานการณ์: ไลน์การผลิตจริง"""
    print("🏭 === จำลองไลน์การผลิต ===")
    print("-" * 35)
    
    sender = JobActionSender()
    
    # จำลองการทำงาน 3 ขั้นตอน
    jobs = [
        {"lot": "PROD-001", "emp": "OP001", "pos": (1, 1)},
        {"lot": "PROD-002", "emp": "OP002", "pos": (1, 2)},
        {"lot": "PROD-003", "emp": "OP003", "pos": (1, 3)},
    ]
    
    # ขั้นตอน 1: PUT ทุกชิ้น
    print("📥 ขั้นตอน 1: วางชิ้นงานทั้งหมด")
    for job in jobs:
        sender.put_job(job["lot"], job["emp"], job["pos"][0], job["pos"][1], "Production-Line")
        time.sleep(1)
    
    print("\n⏳ รอการประมวลผล...")
    time.sleep(3)
    
    # ขั้นตอน 2: GET ทุกชิ้น (บางชิ้นถูก บางชิ้นผิด)
    print("\n📤 ขั้นตอน 2: เอาชิ้นงานออก")
    
    # ชิ้นแรก - ถูก
    sender.get_job("PROD-001", "OP001", 1, 1, "Production-Line")
    time.sleep(1)
    
    # ชิ้นที่สอง - ผิดตำแหน่ง
    sender.get_job("PROD-002", "OP002", 2, 2, "Production-Line")  # ผิด!
    time.sleep(1)
    
    # ชิ้นที่สาม - ถูก
    sender.get_job("PROD-003", "OP003", 1, 3, "Production-Line")

# =====================================================
# เมนูหลัก
# =====================================================

def main_menu():
    print("🎯 ระบบทดสอบ PUT/GET Actions")
    print("=" * 45)
    print("เลือกสถานการณ์ที่ต้องการทดสอบ:")
    print("1. ✅ ทำงานถูกต้อง (PUT → GET ตำแหน่งเดียวกัน)")
    print("2. ❌ เอาชิ้นงานผิดตำแหน่ง")
    print("3. ℹ️  ทดสอบพนักงานต่างกัน (ไม่ตรวจสอบ)")
    print("4. 🏭 จำลองไลน์การผลิต (ผสม)")
    print("5. 🎮 สร้างสถานการณ์เอง")
    print("=" * 45)
    
    choice = input("เลือก (1-5): ")
    
    if choice == "1":
        scenario_correct_workflow()
    elif choice == "2":
        scenario_wrong_position()
    elif choice == "3":
        scenario_wrong_employee()
    elif choice == "4":
        scenario_production_line()
    elif choice == "5":
        interactive_mode()
    else:
        print("❌ เลือกไม่ถูกต้อง")

def interactive_mode():
    """โหมดสร้างสถานการณ์เอง"""
    print("🎮 สร้างสถานการณ์เอง")
    print("-" * 25)
    
    sender = JobActionSender()
    
    while True:
        print("\nเลือกการกระทำ:")
        print("1. PUT (วางชิ้นงาน)")
        print("2. GET (เอาชิ้นงานออก)")
        print("3. ออก")
        
        action_choice = input("เลือก (1-3): ")
        
        if action_choice == "3":
            break
        elif action_choice in ["1", "2"]:
            action = "PUT" if action_choice == "1" else "GET"
            
            lot_no = input("📦 หมายเลข Lot: ")
            emp_id = input("👤 รหัสพนักงาน: ")
            station = input("🏭 สถานี: ") or "Station-A"
            
            try:
                row = int(input("📍 แถว (1-4): "))
                col = int(input("📍 คอลัมน์ (1-6): "))
                
                if action == "PUT":
                    sender.put_job(lot_no, emp_id, row, col, station)
                else:
                    sender.get_job(lot_no, emp_id, row, col, station)
                    
            except ValueError:
                print("❌ กรุณาป้อนตัวเลข")

if __name__ == "__main__":
    main_menu()
    print("\n" + "=" * 45)
    print("✅ ทดสอบเสร็จสิ้น!")
