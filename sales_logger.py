import sys
from datetime import datetime
from sheets_client import get_sheet

def log_sales(input_str):
    # แยกข้อมูลจากรูปแบบ "เมนู:จำนวน:ราคา"
    try:
        menu, qty, price = input_str.split(":")
        qty = int(qty)
        price = float(price)
        total = qty * price
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ส่งข้อมูลเข้า Google Sheets
        sheet = get_sheet()
        sheet.append_row([date_now, menu, qty, price, total])
        print(f"💰 บันทึกยอดขายสำเร็จ: {menu} {qty} แก้ว รวม {total} บาท")
        
    except ValueError:
        print("❌ รูปแบบข้อมูลผิด! กรุณาใช้: 'เมนู:จำนวน:ราคา'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_sales(sys.argv[1])
    else:
        print("กรุณาใส่ข้อมูลยอดขาย เช่น: python sales_logger.py 'ลาเต้:2:60'")