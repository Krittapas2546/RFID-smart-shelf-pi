@echo off
echo 🧹 ทำความสะอาดไฟล์ที่ไม่จำเป็น...
echo.

REM ลบไฟล์ซ้ำซ้อน
echo ❌ ลบไฟล์ job sender เก่า...
del /f /q "my_job_sender.py" 2>nul
del /f /q "job_sender.py" 2>nul

REM ลบไฟล์เซิร์ฟเวอร์เก่า
echo ❌ ลบไฟล์เซิร์ฟเวอร์เก่า...
del /f /q "src\api_server.py" 2>nul
del /f /q "src\job_server.py" 2>nul

REM ลบ template เก่า
echo ❌ ลบ template เก่า...
del /f /q "templates\frontend.html" 2>nul
del /f /q "templates\index.html" 2>nul
del /f /q "templates\test_api.html" 2>nul

REM ลบโฟลเดอร์ซ้ำซ้อน
echo ❌ ลบโฟลเดอร์ static ซ้ำ...
rmdir /s /q "src\static" 2>nul

REM ลบ Python cache
echo ❌ ลบ Python cache...
rmdir /s /q "src\__pycache__" 2>nul
rmdir /s /q "__pycache__" 2>nul

echo.
echo ✅ ทำความสะอาดเสร็จสิ้น!
echo.
echo 📂 ไฟล์ที่เหลือ (จำเป็น):
echo   • src\main.py (เซิร์ฟเวอร์หลัก)
echo   • templates\shelf_ui.html (หน้า UI)
echo   • advanced_job_sender.py (เครื่องมือส่งงาน)
echo   • test_job_sender.py (เครื่องมือทดสอบ)
echo   • requirements.txt (รายการ packages)
echo   • README.md (คู่มือ)
echo   • pkgs\ (Python packages)
echo.
pause
