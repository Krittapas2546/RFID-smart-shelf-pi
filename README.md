# 🏷️ RFID Smart Shelf System

ระบบจัดการชั้นวางอัจฉริยะด้วย RFID สำหรับติดตามชิ้นงานในโรงงาน

## 📋 สารบัญ

- [ติดตั้งระบบ](#-ติดตั้งระบบ)
- [เริ่มใช้งาน](#-เริ่มใช้งาน)
- [การใช้งาน](#-การใช้งาน)
- [การทดสอบ](#-การทดสอบ)
- [API Reference](#-api-reference)
- [แก้ไขปัญหา](#-แก้ไขปัญหา)

---

## 🚀 ติดตั้งระบบ

### ✅ ความต้องการของระบบ

- **Python 3.8+**
- **Windows 10/11** หรือ **Linux**
- **RAM:** 2GB ขึ้นไป
- **เน็ตเวิร์ก:** สำหรับเชื่อมต่อ WebSocket

### 📦 ติดตั้ง Dependencies

```bash
# 1. Clone โปรเจค
git clone https://github.com/your-repo/RFID-smart-shelf-pi.git
cd RFID-smart-shelf-pi

# 2. สร้าง Virtual Environment (แนะนำ)
python -m venv venv

# 3. เปิดใช้งาน Virtual Environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. ติดตั้ง Dependencies
pip install -r requirements.txt
```

---

## 🎯 เริ่มใช้งาน

### 🖥️ เปิดเซิร์ฟเวอร์

#### **วิธีที่ 1: เปิดแบบง่าย**
```bash
cd src
python main.py
```

#### **วิธีที่ 2: เปิดแบบ Development**
```bash
# จากโฟลเดอร์รูท
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### ✅ ตรวจสอบว่าเซิร์ฟเวอร์ทำงาน

เมื่อเซิร์ฟเวอร์เริ่มทำงาน คุณจะเห็นข้อความ:

```
INFO: Started server process [XXXX]
🚀 Job socket server started on port 8000
RFID reader process disabled - ready for external job data.
INFO: Uvicorn running on http://0.0.0.0:8001
```

---

## 🌐 การใช้งาน

### 📱 หน้าเว็บระบบ

| หน้า | URL | คำอธิบาย |
|------|-----|----------|
| **หน้าหลัก** | http://localhost:8001 | UI สำหรับติดตามชั้นวางและคิวงาน |
| **Test Console** | http://localhost:8001/test | เครื่องมือทดสอบระบบ |
| **API Docs** | http://localhost:8001/docs | เอกสาร API (Swagger) |

### 🔌 พอร์ตที่ใช้งาน

| พอร์ต | หน้าที่ | คำอธิบาย |
|-------|---------|----------|
| **8000** | Socket Server | รับข้อมูล Job จากระบบภายนอก |
| **8001** | Web Server | เสิร์ฟหน้าเว็บและ API |

---

## 🧪 การทดสอบ

### 🎮 ใช้ Test Console (แนะนำ)

1. **เปิดหน้า Test Console:** http://localhost:8001/test
2. **เลือกสถานการณ์ทดสอบ:**
   - ✅ **ทำถูก** - PUT และ GET ตำแหน่งเดียวกัน
   - ❌ **ผิดตำแหน่ง** - PUT ที่หนึ่ง GET ที่อื่น
   - 🔄 **PUT ซ้ำ** - วาง Lot เดิมซ้ำ
   - 🔍 **GET ไม่เจอ** - เอา Lot ที่ไม่มี

### 📝 ใช้ Python Scripts

#### **ทดสอบพื้นฐาน:**
```bash
python test_job_sender.py
```

#### **ทดสอบขั้นสูง:**
```bash
python advanced_job_sender.py
# เลือก:
# 1 = ส่งงานตัวอย่าง
# 2 = จำลองไลน์การผลิต
# 3 = จำลอง Quality Control
# 4 = โหมดโต้ตอบ
```

#### **ทดสอบ PUT/GET Actions:**
```bash
python action_test_sender.py
# เลือก:
# 1 = ทดสอบทำถูก
# 2 = ทดสอบผิดตำแหน่ง
# 3 = ทดสอบคนต่างกัน (จะสำเร็จ)
```

---

## 🔧 การพัฒนาและปรับแต่ง

### 📁 โครงสร้างไฟล์

```
RFID-smart-shelf-pi/
├── src/
│   ├── main.py              # เซิร์ฟเวอร์หลัก
│   └── static/              # ไฟล์ CSS/JS
├── templates/
│   ├── shelf_ui.html        # หน้า UI หลัก
│   └── test_console.html    # หน้า Test Console
├── test_job_sender.py       # ทดสอบพื้นฐาน
├── advanced_job_sender.py   # ทดสอบขั้นสูง
├── action_test_sender.py    # ทดสอบ PUT/GET
├── requirements.txt         # Dependencies
└── README.md               # คู่มือนี้
```

### 🛠️ การส่งข้อมูล Job

ระบบรับข้อมูล JSON ในรูปแบบ:

```json
{
    "action": "PUT",           // PUT หรือ GET
    "status": "Waiting",       // สถานะเริ่มต้น
    "lotNo": "LOT-001",       // หมายเลข Lot
    "from": "Station-A",       // สถานีต้นทาง
    "employeeId": "EMP001",    // รหัสพนักงาน
    "location": {
        "row": 1,              // แถว (1-4)
        "col": 1               // คอลัมน์ (1-6)
    },
    "timestamp": "14:30:15",   // เวลา
    "error": null              // ข้อผิดพลาด (null = ไม่มี)
}
```

### 📡 การส่งข้อมูลผ่าน Socket

```python
import socket
import json

def send_job(job_data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 8000))
        message = json.dumps(job_data).encode('utf-8')
        sock.sendall(message)
        response = sock.recv(1024).decode('utf-8')
        print(f"Server response: {response}")
```

---

## 📊 Logic การทำงาน

### 🔄 PUT Action (วางชิ้นงาน)

| เงื่อนไข | ผลลัพธ์ | สถานะ |
|----------|---------|-------|
| Lot ยังไม่มีในระบบ | ✅ สำเร็จ - เข้าคิว | `Waiting` |
| Lot มีอยู่แล้ว | ❌ ผิดพลาด - ไม่เข้าคิว | `Error` |

### 📤 GET Action (เอาชิ้นงานออก)

| เงื่อนไข | ผลลัพธ์ | สถานะ |
|----------|---------|-------|
| Lot ไม่มีในระบบ | ❌ ผิดพลาด - ไม่ทำอะไร | `Error` |
| Lot มี + ตำแหน่งถูก | ✅ สำเร็จ - ออกจากคิว | `Completed` |
| Lot มี + ตำแหน่งผิด | ❌ ผิดพลาด - ค้างในคิว | `Error` |

### 🎯 การจัดการคิว

- **1 งานในคิว** → เลือกอัตโนมัติ
- **หลายงานในคิว** → แสดงให้เลือก
- **งานที่ Error** → ค้างในคิวพร้อมแสดงข้อผิดพลาด
- **งานที่สำเร็จ** → ออกจากคิวทันที

---

## 🛑 การปิดระบบ

### วิธีที่ 1: กด Ctrl+C
```
ใน Terminal ที่เซิร์ฟเวอร์ทำงาน กด Ctrl + C
```

### วิธีที่ 2: ปิดผ่าน Process
```bash
# Windows
tasklist | findstr python
taskkill /PID [PID_NUMBER] /F

# Linux/Mac
ps aux | grep python
kill -9 [PID_NUMBER]
```

---

## ⚠️ แก้ไขปัญหา

### 🔴 ปัญหาที่พบบ่อย

#### **1. Port ถูกใช้งานแล้ว**
```bash
# ตรวจสอบและปิด process ที่ใช้ port
netstat -ano | findstr :8001
taskkill /PID [PID] /F
```

#### **2. WebSocket ไม่เชื่อมต่อ**
- ตรวจสอบว่าเซิร์ฟเวอร์ทำงานที่ port 8001
- ลองรีเฟรชหน้าเบราว์เซอร์
- เช็ค Console ใน Browser (F12)

#### **3. ไม่มี Templates Directory**
```bash
# สร้างโฟลเดอร์ templates ถ้าไม่มี
mkdir templates
# หรือ
mkdir src/templates
```

#### **4. การเชื่อมต่อ Socket ล้มเหลว**
- ตรวจสอบว่าเซิร์ฟเวอร์ทำงานที่ port 8000
- ลองเปลี่ยน IP เป็น '127.0.0.1' แทน 'localhost'
- ตรวจสอบ Firewall

### 📝 Logs การทำงาน

เซิร์ฟเวอร์จะแสดง logs ในรูปแบบ:
```
2024-06-26 16:30:15,123 - INFO - 📥 Received job data:
2024-06-26 16:30:15,124 - INFO - PUT Success: LOT-001 placed at (1,1)
2024-06-26 16:30:15,125 - INFO - ✅ Job data processed and added to queue
```

---

## 🎯 Keyboard Shortcuts (Test Console)

| คีย์ | การทำงาน |
|-----|----------|
| `Ctrl + 1` | ส่ง PUT |
| `Ctrl + 2` | ส่ง GET |
| `Ctrl + 3` | ทดสอบทำถูก |
| `Ctrl + 4` | ทดสอบผิดตำแหน่ง |
| `Ctrl + Del` | ล้างคิว |

---

## 📞 ติดต่อและสนับสนุน

- **เอกสาร API:** http://localhost:8001/docs
- **GitHub Issues:** [สร้าง Issue ใหม่](https://github.com/your-repo/RFID-smart-shelf-pi/issues)
- **การพัฒนา:** ดู `src/main.py` สำหรับ logic หลัก

---

## 📈 การพัฒนาต่อ

### 🔮 ฟีเจอร์ที่วางแผน:
- [ ] การเชื่อมต่อ RFID Reader จริง
- [ ] Database สำหรับเก็บประวัติ
- [ ] การแจ้งเตือนผ่าน Email/LINE
- [ ] Dashboard สำหรับผู้จัดการ
- [ ] Mobile App

### 🛠️ การ Customize:
- แก้ไขขนาดกริด: เปลี่ยนค่าใน `shelf_ui.html`
- เพิ่มสี: แก้ไข CSS ใน `<style>` section
- เพิ่ม API: เพิ่ม route ใน `main.py`

---

*อัปเดตล่าสุด: มิถุนายน 2024*

