import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_sheets_client():
    # ดึงค่าจาก Environment Variables (Secrets ใน GitHub)
    service_account_info = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))
    
    # กำหนดสิทธิ์การเข้าถึง
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # สร้าง Credentials
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    
    # เชื่อมต่อกับ gspread
    client = gspread.authorize(creds)
    return client

def get_sheet_data(spreadsheet_id, range_name):
    client = get_sheets_client()
    sh = client.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(0) # ดึงหน้าแรก
    return worksheet.get_all_records()