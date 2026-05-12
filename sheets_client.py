import json
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

# กำหนดสิทธิ์การเข้าถึง
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet():
    """ฟังก์ชันสำหรับเชื่อมต่อ Google Sheets"""
    # ตรวจสอบว่ารันบนเครื่อง (File) หรือรันบน GitHub Actions (JSON string)
    json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    file_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

    if json_str:
        info = json.loads(json_str)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    elif file_path:
        creds = Credentials.from_service_account_file(file_path, scopes=SCOPES)
    else:
        raise RuntimeError("ไม่พบ GOOGLE_SERVICE_ACCOUNT_JSON หรือ FILE ใน .env")

    # เชื่อมต่อและเปิด Sheet ด้วย ID
    client = gspread.authorize(creds)
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    return client.open_by_key(sheet_id).sheet1

if __name__ == "__main__":
    try:
        get_sheet()
        print("✅ เชื่อมต่อ Google Sheets สำเร็จ!")
    except Exception as e:
        print(f"❌ เชื่อมต่อไม่สำเร็จเนื่องจาก: {e}")