import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// กำหนดขนาดของ Grid ตามโค้ด Tkinter เดิมของคุณ
const ROWS = 4;
const COLS = 6;

function App() {
  // State สำหรับเก็บข้อมูลของชั้นวางทั้งหมดที่ได้จาก API
  const [shelfState, setShelfState] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // ฟังก์ชันสำหรับดึงข้อมูลจาก Backend
    const fetchItems = async () => {
      try {
        // ใช้ IP ของเครื่องที่รัน Backend หรือ 127.0.0.1 ถ้าทดสอบบนเครื่องเดียวกัน
        const response = await axios.get('http://127.0.0.1:8000/api/shelf-state');
        setShelfState(response.data);
      } catch (err) {
        setError('ไม่สามารถเชื่อมต่อกับ API Server ได้ กรุณาตรวจสอบว่า Server ทำงานอยู่');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    // ดึงข้อมูลครั้งแรกทันที
    fetchItems();
    // ตั้งค่าให้ดึงข้อมูลซ้ำทุกๆ 2 วินาที (Polling) เพื่ออัปเดตหน้าจอแบบ real-time
    const intervalId = setInterval(fetchItems, 2000);

    // Cleanup function: ยกเลิกการ polling เมื่อ component ถูกปิด
    return () => clearInterval(intervalId);
  }, []); // dependency array ที่ว่างเปล่า หมายถึงให้ run effect นี้แค่ครั้งเดียว

  // ฟังก์ชันสำหรับสร้างและแสดงผล Grid
  const renderGrid = () => {
    const grid = [];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const key = `${r},${c}`;
        const itemData = shelfState[key]; // ดึงข้อมูลของช่องนี้จาก state

        let cellContent;
        let cellClass = "shelf-item";

        if (itemData) {
            // ถ้ามีข้อมูลในช่องนี้, สร้างข้อความที่จะแสดง
            const details_text = Object.entries(itemData)
                .filter(([key, value]) => key !== 'location' && key !== 'PositionSTK') // ไม่ต้องแสดงข้อมูล location ซ้ำ
                .map(([key, value]) => `${key}: ${value}`)
                .join('\n');

            cellContent = (
                <>
                    <span className="item-details" style={{ whiteSpace: 'pre-wrap' }}>
                        {details_text || "กำลังประมวลผล..."}
                    </span>
                    <span className="item-id">({r},{c})</span>
                </>
            );
            cellClass += ' occupied'; // เพิ่ม class 'occupied'
        } else {
            // ถ้าไม่มีข้อมูล (ช่องว่าง)
            cellContent = (
                <>
                    <span className="item-name">Empty</span>
                    <span className="item-id">({r},{c})</span>
                </>
            );
            cellClass += " empty";
        }

        grid.push(
            <div key={key} className={cellClass}>
                {cellContent}
            </div>
        );
      }
    }
    return grid;
  };

  if (loading && Object.keys(shelfState).length === 0) {
    return <div className="status-message">กำลังโหลดข้อมูลชั้นวาง...</div>;
  }

  if (error) {
    return <div className="status-message error">{error}</div>;
  }

  return (
    <div className="App">
      <h1>RFID Smart Shelf - Web UI</h1>
      <div className="shelf-container">
        <div className="shelf-grid">
          {renderGrid()}
        </div>
      </div>
    </div>
  );
}

export default App;