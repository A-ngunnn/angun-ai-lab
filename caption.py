# Caption generator for MilkLab cafe Instagram posts
# - Load GOOGLE_API_KEY from .env file
# - Use Gemini 2.5 Flash to generate 3 caption variants
# - Take menu name and price as input
# - Output: 3 caption styles (cute, minimal, gen-z)

import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("❌ ไม่พบ GOOGLE_API_KEY ในไฟล์ .env")
    exit(1)

# Initialize the Gemini model
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "models/gemini-2.5-flash"

PROMPT_TEMPLATE = (
    "สร้างแคปชั่น Instagram แบบ 3 สไตล์ สำหรับร้าน MilkLab cafe (ใช้ภาษาไทยแบบเป็นกันเอง)\n"
    "ใจความ: เมนูคือ '{menu_name}' ราคา {price} บาท\n"
    "ขอให้เขียน 3 สไตล์นี้:\n"
    "1. สไตล์น่ารัก - อบอุ่น สนุกสนาน เต็มไปด้วยอีโมจิ เหมือนคุยกับเพื่อนสนิท\n"
    "2. สไตล์มินิมัล - สั้นๆ หรูหรา ประณีต ดูเท่\n"
    "3. สไตล์เจน-ซี - ทันสมัย ไม่เป็นทางการ ชวนหัวเราะ\n"
    "ให้เขียนแยกเป็น 3 ข้อหลัก โดยตั้งหัวข้อว่า:\n"
    "1. น่ารัก\n"
    "2. มินิมัล\n"
    "3. เจน-ซี\n"
)

STYLE_LABELS = ["น่ารัก", "มินิมัล", "เจน-ซี"]


def generate_captions(menu_name: str, price: str) -> str:
    prompt = PROMPT_TEMPLATE.format(menu_name=menu_name, price=price)
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return getattr(response, "text", str(response)).strip()


def parse_captions(raw_text: str) -> list[str]:
    parts = re.split(r"\n\s*\d+\.?\s*", raw_text.strip())
    captions = [part.strip() for part in parts if part.strip()]
    if len(captions) >= 3:
        return captions[:3]
    return [raw_text.strip()]


def main() -> None:
    print("--- 🥛 MilkLab Caption Generator ☕ ---")
    menu_name = input("✍️  วันนี้มีเมนูอะไรใหม่คะ?: ").strip()
    price = input("💰 ราคาเท่าไหร่เอ่ย?: ").strip()

    if not menu_name or not price:
        print("⚠️ ใส่ข้อมูลไม่ครบถ้วนนะคะ")
        return

    print("\n🚀 กำลังติดต่อ AI... รอสักครู่นะ")
    print("-" * 60)
    raw_result = generate_captions(menu_name, price)
    captions = parse_captions(raw_result)

    print(f"✨ ได้แคปชั่นสำหรับ {menu_name} ({price} บาท) แล้วยา! ✨\n")
    for idx, caption in enumerate(captions, start=1):
        label = STYLE_LABELS[idx - 1] if idx <= len(STYLE_LABELS) else f"สไตล์ {idx}"
        print(f"📸 สไตล์{label}:")
        print(f"{caption}\n")

    print("-" * 60)


if __name__ == "__main__":
    main()
