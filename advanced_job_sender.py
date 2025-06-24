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

def send_production_batch():
    """จำลองการส่งงานจากไลน์การผลิต"""
    print("🏭 จำลองงานจากไลน์การผลิต")
    print("-" * 30)
    
    # Batch งานจากไลน์ A
    production_jobs = [
        {"lot": "PROD-A-001", "emp": "OP001", "station": "Line-A", "pos": (1, 1)},
        {"lot": "PROD-A-002", "emp": "OP001", "station": "Line-A", "pos": (1, 2)},
        {"lot": "PROD-A-003", "emp": "OP001", "station": "Line-A", "pos": (1, 3)},
    ]
    
    for job in production_jobs:
        send_custom_job(job["lot"], job["emp"], job["station"], job["pos"][0], job["pos"][1])
        time.sleep(1)  # หน่วงเวลา 1 วินาที

def send_qc_jobs():
    """จำลองงาน Quality Control"""
    print("🔍 จำลองงาน Quality Control")
    print("-" * 30)
    
    qc_jobs = [
        {"lot": "QC-001", "emp": "QC001", "station": "QC-Station", "pos": (2, 1)},
        {"lot": "QC-002", "emp": "QC002", "station": "QC-Station", "pos": (2, 2)},
    ]
    
    for job in qc_jobs:
        send_custom_job(job["lot"], job["emp"], job["station"], job["pos"][0], job["pos"][1])
        time.sleep(1)

def interactive_mode():
    """โหมดโต้ตอบ - ให้ผู้ใช้ป้อนข้อมูลเอง"""
    print("🎮 โหมดโต้ตอบ - ป้อนข้อมูลงานเอง")
    print("-" * 40)
    
    while True:
        print("\nป้อนข้อมูลงาน (หรือพิมพ์ 'exit' เพื่อออก):")
        
        lot_no = input("📦 หมายเลข Lot: ")
        if lot_no.lower() == 'exit':
            break
            
        emp_id = input("👤 รหัสพนักงาน: ")
        station = input("🏭 สถานี (เว้นว่างใช้ Station-A): ") or "Station-A"
        
        try:
            row = int(input("📍 แถว (1-4): ") or 1)
            col = int(input("📍 คอลัมน์ (1-6): ") or 1)
        except ValueError:
            print("❌ กรุณาป้อนตัวเลข")
            continue
            
        success = send_custom_job(lot_no, emp_id, station, row, col)
        if success:
            print("✅ ส่งงานเสร็จเรียบร้อย!")
        else:
            print("❌ ส่งงานไม่สำเร็จ")

# เมนูหลัก
if __name__ == "__main__":
    print("🎯 ระบบส่งงาน Smart Shelf")
    print("=" * 40)
    print("เลือกโหมดการทำงาน:")
    print("1. ส่งงานตัวอย่าง (3 งาน)")
    print("2. จำลองงานไลน์การผลิต")
    print("3. จำลองงาน Quality Control")  
    print("4. โหมดโต้ตอบ (ป้อนข้อมูลเอง)")
    print("=" * 40)
    
    choice = input("เลือก (1-4): ")
    
    if choice == "1":
        # ส่งงานตัวอย่าง
        send_custom_job("LOT-001", "EMP001", "Station-A", 1, 1)
        send_custom_job("LOT-002", "EMP002", "Station-B", 2, 3)
        send_custom_job("LOT-003", "EMP003", "Station-C", 4, 6)
        
    elif choice == "2":
        send_production_batch()
        
    elif choice == "3":
        send_qc_jobs()
        
    elif choice == "4":
        interactive_mode()
        
    else:
        print("❌ เลือกไม่ถูกต้อง")
    
    print("=" * 40)
    print("✅ เสร็จสิ้น!")
