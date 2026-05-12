import os
import requests
from dotenv import load_dotenv
from sheets_client import get_sheet

# โหลดค่าจาก .env
load_dotenv()

def send_telegram_msg(message):
    """ฟังก์ชันส่งข้อความเข้า Telegram"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการส่ง: {e}")

def generate_report():
    """สรุปยอดจาก Sheet แล้วส่งรายงาน"""
    sheet = get_sheet()
    data = sheet.get_all_records()
    
    if not data:
        send_telegram_msg("📊 *MilkLab Report*: ยังไม่มีข้อมูลการขายจ้า")
        return

    # รวมยอดขายทั้งหมด
    total_sales = sum(float(row['ยอดรวม']) for row in data)
    
    report_msg = (
        "🥤 *MilkLab Cafe Daily Report*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💰 *ยอดขายรวม:* `{total_sales:,.2f}` บาท\n"
        f"📑 *จำนวนรายการ:* `{len(data)}` รายการ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "วันนี้ขายดี ขอให้รวยๆ ครับ! 🚀"
    )
    
    send_telegram_msg(report_msg)
    print("✅ ส่งรายงานไปที่ Telegram เรียบร้อยแล้ว!")

if __name__ == "__main__":
    generate_report()