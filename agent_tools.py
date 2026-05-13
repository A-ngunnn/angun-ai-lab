# agent_tools.py
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

def get_sheets_client():
    """เชื่อมต่อกับ Google Sheets API"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # ใช้ไฟล์ service-account.json ตามที่คุณตั้งค่าใน .env
    creds = Credentials.from_service_account_file(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"), 
        scopes=scopes
    )
    return gspread.authorize(creds)

def validate_sale(menu: str, quantity: int, price: float) -> None:
    if not menu or not menu.strip():
        raise ValueError("ชื่อเมนูห้ามว่าง")
    if quantity <= 0:        
        raise ValueError("จำนวนต้องมากกว่า 0")
    if price <= 0:           
        raise ValueError("ราคาต้องมากกว่า 0")

def send_telegram(message: str):
    """ส่งข้อความเข้า Telegram"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

def log_sale(menu: str, quantity: int, price: float) -> dict:
    """ฟังก์ชันหลัก: ตรวจสอบ -> บันทึกลงชีต -> ส่ง Telegram"""
    validate_sale(menu, quantity, price)
    total = quantity * price
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 1. บันทึกลง Google Sheets
        client = get_sheets_client()
        sheet = client.open_by_key(os.getenv("GOOGLE_SHEETS_ID")).get_worksheet(0)
        sheet.append_row([timestamp, menu, quantity, price, total])

        # 2. ส่ง Telegram
        msg = f"✅ บันทึกยอดขายใหม่!\n📋 เมนู: {menu}\n🔢 จำนวน: {quantity}\n💰 รวม: {total} บาท"
        send_telegram(msg)

        return {
            "status": "success",
            "menu": menu,
            "quantity": quantity,
            "price": price,
            "total": total,
            "timestamp": timestamp
        }
    except Exception as e:
        raise RuntimeError(f"เกิดข้อผิดพลาดในการเชื่อมต่อระบบภายนอก: {str(e)}")

TOOLS = {
    "log_sale": log_sale,
}