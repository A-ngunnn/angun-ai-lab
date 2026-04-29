# สร้างโปรแกรมรับชื่อเมนูและราคาจาก user แล้วใช้ Gemini AI ช่วยแต่ง Caption Instagram ภาษาไทยให้ร้าน A-Ngun Cafe

import os
from dotenv import load_dotenv
import google.generativeai as genai

# โหลด environment variables
load_dotenv()

# ตั้งค่า API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ อย่าลืมใส่ GOOGLE_API_KEY ในไฟล์ .env นะคะ")
    exit(1)

genai.configure(api_key=api_key)

def get_available_model():
    """เลือกโมเดลที่ฉลาดและว่างที่สุด"""
    try:
        # พยายามใช้ 1.5 flash เพราะเป็นมิตรกับสายฟรีที่สุด
        return 'gemini-1.5-flash'
    except:
        return 'gemini-pro'

model = genai.GenerativeModel(get_available_model())

def generate_instagram_caption(menu_name: str, price: str) -> str:
    """ใช้ AI ช่วยเสกแคปชั่นน่ารักๆ"""
    
    prompt = f"""
    คุณเป็น Content Creator มืออาชีพ ช่วยเขียนแคปชั่น Instagram ภาษาไทยให้ร้าน "A-Ngun Cafe"
    เมนูคือ: {menu_name} ราคา: {price} บาท
    
    โจทย์:
    - ภาษาวัยรุ่น น่ารัก เป็นกันเอง
    - มีอีโมจิเยอะๆ ให้ดูสดใส
    - ชวนคนให้อยากมาลองดื่ิมที่ร้าน
    - ติดแฮชแท็ก #ANGunCafe #คาเฟ่เปิดใหม่ และแฮชแท็กที่เกี่ยวกับเมนู
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            # คำที่คนทั่วไปใช้เวลา AI ไม่ว่างตอบ
            return "ขออภัยน้าา ตอนนี้คนใช้ AI เยอะมากกก จนคิดแคปชั่นไม่ทัน 😅\nรบกวนรอสัก 1 นาที แล้วลองกดรันใหม่อีกรอบนะคะ! 🙏✨"
        else:
            return "อุ๊ย! ระบบขัดข้องนิดหน่อย ลองตรวจสอบอินเทอร์เน็ตหรือ API Key อีกครั้งนะคะ 🛠️"

def main():
    print("--- 🍇 A-Ngun Cafe: Instagram Caption Generator 🍇 ---")
    
    menu_name = input("✍️  ชื่อเมนูวันนี้คืออะไรคะ?: ").strip()
    price = input("💰 ราคาเท่าไหร่เอ่ย?: ").strip()

    if not menu_name or not price:
        print("⚠️  ใส่ข้อมูลไม่ครบ AI ไปต่อไม่ถูกเลยน้าา")
        return

    print("\n🚀 กำลังส่งข้อมูลให้ AI ช่วยคิด... รอสักครู่นะคะ")
    print("-" * 50)

    caption = generate_instagram_caption(menu_name, price)

    print("✨ แคปชั่นที่ได้คือ: ✨")
    print(caption)
    print("-" * 50)

if __name__ == "__main__":
    main()