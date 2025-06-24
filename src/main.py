import multiprocessing
import socket
import json
from queue import Empty
import tkinter as tk

# =============================================================================
# 1. Server Process: รอรับข้อมูลจาก Client (เช่น api_test.py)
# =============================================================================
def server_process(job_queue, host='0.0.0.0', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"✅ Server listening on {host}:{port}")
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    print(f"🤝 Connected by {addr}")
                    data = conn.recv(4096)
                    if not data:
                        continue

                    # สมมติว่าข้อมูลที่เข้ามาอาจมีหลาย JSON object ต่อกัน
                    decoded_data = data.decode('utf-8')
                    # แยก JSON objects ที่อาจจะติดกันมา
                    for job_str in decoded_data.strip().split('}'):
                        if not job_str.strip():
                            continue
                        try:
                            # เพิ่ม '}' กลับเข้าไปเพื่อให้เป็น JSON ที่สมบูรณ์
                            full_job_str = job_str + '}'
                            job = json.loads(full_job_str)
                            print(f"📥 Received Full Job Data:\n{json.dumps(job, indent=2)}")
                            job_queue.put(job)
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON Decode Error: {e} for data: '{job_str}'")

            except Exception as e:
                print(f"An error occurred in server process: {e}")


# =============================================================================
# 2. UI Process: สร้างหน้าจอและอัปเดตข้อมูลจาก Queue
# =============================================================================
def ui_process(job_queue):
    root = tk.Tk()
    root.title("Automated Warehouse Shelf - Detailed View")
    root.geometry("1600x900")

    rows, cols = 5, 10
    shelf_labels = [[None for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            frame = tk.Frame(root, width=150, height=100, borderwidth=1, relief="solid")
            frame.grid(row=r, column=c, padx=5, pady=5)
            frame.pack_propagate(False)

            # ใช้ f-string ที่ถูกต้องสำหรับข้อความเริ่มต้น
            initial_text = f"({r},{c})\nEmpty"
            details_label = tk.Label(
                frame,
                text=initial_text,
                font=("Arial", 8),
                justify=tk.LEFT,
                wraplength=140,
                bg="#f0f0f0" # สีพื้นหลังเริ่มต้น
            )
            details_label.pack(fill="both", expand=True, padx=2, pady=2)
            shelf_labels[r][c] = {'details': details_label}

    def check_for_jobs():
        try:
            job = job_queue.get_nowait()
            print(f"🎨 UI updating with data: {job}")

            location_data = job.get("location")
            action = job.get("action", "PUT").upper() # ตั้งค่าเริ่มต้นเป็น PUT และแปลงเป็นตัวพิมพ์ใหญ่

            if isinstance(location_data, dict):
                row = location_data.get("row")
                col = location_data.get("col")

                # ตรวจสอบว่าพิกัดถูกต้องและอยู่ในขอบเขต
                if isinstance(row, int) and isinstance(col, int) and (0 <= row < rows and 0 <= col < cols):
                    target_label = shelf_labels[row][col]['details']

                    if action == "PUT":
                        # สร้างข้อความรายละเอียดจากข้อมูล Job
                        details_text = ""
                        for key, value in job.items():
                            # ไม่แสดงข้อมูลที่ไม่จำเป็นใน UI
                            if key in ["location", "PositionSTK"]:
                                continue
                            details_text += f"{key}: {value}\n"
                        details_text = details_text.strip()

                        target_label.config(
                            text=details_text,
                            fg="black",
                            bg="#e0e8ff"  # สีฟ้าอ่อนสำหรับของที่เข้ามาใหม่
                        )
                    else:  # สำหรับ action อื่นๆ เช่น GET, MOVE หรือเมื่อนำของออก
                        target_label.config(
                            text=f"({row},{col})\nEmpty", # คืนค่าเป็น Empty
                            fg="black",
                            bg="#f0f0f0"  # คืนค่าสีพื้นหลังเป็นสีเทาอ่อน
                        )
                else:
                    print(f"⚠️ Invalid location coordinates: (row={row}, col={col})")
            else:
                print(f"⚠️ Job is missing 'location' key or it's not a dictionary: {job}")

        except Empty:
            pass
        finally:
            root.after(100, check_for_jobs)

    print("✅ UI process started.")
    check_for_jobs()
    root.mainloop()



if __name__ == "__main__":
    print("🚀 Starting Main Application...")
    job_queue = multiprocessing.Queue()

    p_server = multiprocessing.Process(target=server_process, args=(job_queue,), daemon=True)
    p_ui = multiprocessing.Process(target=ui_process, args=(job_queue,))

    p_server.start()
    p_ui.start()

    p_ui.join()
    print("UI process finished. Exiting application.")