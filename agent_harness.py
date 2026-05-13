# agent_harness.py
import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

from agent_tools import TOOLS

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash")

SYSTEM_INSTRUCTION = """
คุณคือ Demi ผู้ช่วย AI ของร้าน MilkLab°
หน้าที่ของนักศึกษาคือแปลงคำสั่งภาษาไทยเป็น JSON action
ตอบกลับเป็น JSON เท่านั้น ในรูปแบบ:
{"action": "log_sale", "args": {"menu": "...", "quantity": N, "price": N}}
ถ้าคำสั่งไม่ใช่การบันทึกยอดขาย ตอบ: {"action": "unknown", "args": {}}
"""

TRACE_FILE = "agent_trace.log"


def write_trace(event: str, data: dict) -> None:
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data,
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _format_genai_error(exc: genai_errors.ClientError) -> tuple[str | int | None, str, dict]:
    code = getattr(exc, "code", None) or getattr(exc, "status", None)
    if code is None and exc.args:
        code = exc.args[0]

    response_json = None
    if len(exc.args) > 1 and isinstance(exc.args[1], dict):
        response_json = exc.args[1]

    error_message = None
    if response_json:
        error_message = response_json.get("error", {}).get("message")
    if not error_message:
        error_message = str(exc)

    return code, error_message, response_json or {}


def parse_sale_input(user_input: str) -> dict | None:
    text = user_input.strip()
    if not text:
        return None

    if re.match(r"^\d+(?:\.\d+)?$", text):
        return {
            "action": "log_sale_price_only",
            "args": {"price_or_qty": float(text) if "." in text else int(text)},
        }

    if text and not any(c.isdigit() for c in text):
        return {
            "action": "log_sale_menu_only",
            "args": {"menu": text},
        }

    patterns = [
        r"(?P<menu>.+?)\s*(?:x|X)\s*(?P<qty>\d+)\s*(?P<price>\d+(?:\.\d+)?)\s*บาท",
        r"(?P<menu>.+?)\s*(?P<qty>\d+)\s*(?:แก้ว|ถ้วย|ชิ้น|ใบ|ที่)\s*(?:ราคา\s*)?(?P<price>\d+(?:\.\d+)?)\s*บาท",
        r"(?P<menu>.+?)\s*(?P<price>\d+(?:\.\d+)?)\s*บาท",
        r"(?P<menu>.+?)\s*(?:x|X)\s*(?P<qty>\d+)\s*(?P<price>\d+(?:\.\d+)?)",
        r"(?P<menu>.+?)\s*(?P<qty>\d+)\s*(?:แก้ว|ถ้วย|ชิ้น|ใบ|ที่)\s*(?:ราคา\s*)?(?P<price>\d+(?:\.\d+)?)",
        r"(?P<menu>.+?)\s*(?:ราคา\s*)?(?P<price>\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue

        menu = match.group("menu").strip()
        price = match.groupdict().get("price")
        qty = match.groupdict().get("qty")

        if not menu or not price:
            continue

        quantity = int(qty) if qty else 1
        price_value = float(price) if "." in price else int(price)

        return {
            "action": "log_sale",
            "args": {
                "menu": menu,
                "quantity": quantity,
                "price": price_value,
            },
        }

    return None


def _format_success_message(result: dict) -> str:
    """Format successful tool result into user message with defensive access"""
    menu = result.get("menu", "?")
    quantity = result.get("quantity", 1)
    total = result.get("total", 0)
    return f"✅ บันทึกสำเร็จ: {menu} x{quantity} = {total} บาท"


def execute_action(action_data: dict) -> str:
    action = action_data.get("action")
    args = action_data.get("args", {})

    if action == "log_sale_menu_only":
        menu = args.get("menu", "")
        write_trace("fallback_incomplete", {"type": "menu_only", "menu": menu})
        return f"ชื่อเมนู: {menu} 💭\nกรุณาพิมพ์ราคา (เช่น '45') หรือรูปแบบสมบูรณ์ (เช่น '{menu} 45 บาท')"

    if action == "log_sale_price_only":
        price_or_qty = args.get("price_or_qty", 0)
        write_trace("fallback_incomplete", {"type": "price_only", "price_or_qty": price_or_qty})
        return f"ราคา/จำนวน: {price_or_qty} 🤔\nกรุณาพิมพ์ชื่อเมนูและราคา (เช่น 'ลาเต้ 45 บาท')"

    if action not in TOOLS:
        return f"⚠️ ไม่รู้จัก action: {action}"

    try:
        result = TOOLS[action](**args)
        write_trace("tool_result", {"action": action, "result": result})
        return _format_success_message(result)
    except (ValueError, TypeError, KeyError) as e:
        write_trace("tool_error", {"action": action, "error": str(e)})
        return f"❌ ข้อมูลไม่ถูกต้อง: {e}"
    except Exception as e:
        write_trace("tool_error", {"action": action, "error": f"Unexpected error: {str(e)}"})
        return f"❌ เกิดข้อผิดพลาด: {e}"


def run_agent(user_input: str) -> str:
    write_trace("user_input", {"message": user_input})

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"{SYSTEM_INSTRUCTION}\n\nคำสั่ง: {user_input}",
        )
    except genai_errors.ClientError as exc:
        code, error_message, response_json = _format_genai_error(exc)
        write_trace("llm_error", {
            "code": code,
            "message": error_message,
            "response": response_json,
        })

        if str(code) == "429" or str(code) == "RESOURCE_EXHAUSTED":
            fallback_data = parse_sale_input(user_input)
            if fallback_data:
                write_trace("fallback_parse", {"input": user_input, "action_data": fallback_data})
                return execute_action(fallback_data)

            retry_delay = None
            details = response_json.get("error", {}).get("details", [])
            for item in details:
                if isinstance(item, dict) and item.get("@type", "").endswith("RetryInfo"):
                    retry_delay = item.get("retryDelay")
                    break

            if retry_delay:
                return (
                    "❌ โควต้าหมดแล้ว: กรุณาตรวจสอบการตั้งค่าแผนและการเรียกเก็บเงินของคุณ "
                    f"หรือรอ {retry_delay} แล้วลองใหม่อีกครั้ง"
                )

            return (
                "❌ โควต้าหมดแล้ว: กรุณาตรวจสอบการตั้งค่าแผนและการเรียกเก็บเงินของคุณ "
                "หรือรอเวลาที่แนะนำก่อนลองใหม่อีกครั้ง"
            )

        return f"❌ เกิดข้อผิดพลาดจาก LLM: {error_message}"

    raw = response.text.strip()
    write_trace("llm_response", {"raw": raw})

    try:
        action_data = json.loads(raw)
    except json.JSONDecodeError:
        return "❌ AI ตอบกลับในรูปแบบที่ไม่ถูกต้อง"

    action = action_data.get("action")
    args = action_data.get("args", {})

    if action not in TOOLS:
        return f"⚠️ ไม่รู้จัก action: {action}"

    try:
        result = TOOLS[action](**args)
        write_trace("tool_result", {"action": action, "result": result})
        return _format_success_message(result)
    except (ValueError, TypeError, KeyError) as e:
        write_trace("tool_error", {"action": action, "error": str(e)})
        return f"❌ ข้อมูลไม่ถูกต้อง: {e}"
    except Exception as e:
        write_trace("tool_error", {"action": action, "error": f"Unexpected error: {str(e)}"})
        return f"❌ เกิดข้อผิดพลาด: {e}"


if __name__ == "__main__":
    print("Demi Agent พร้อมรับคำสั่ง (พิมพ์ 'exit' เพื่อออก)\n")
    while True:
        user_input = input("คุณ: ").strip()
        if user_input.lower() == "exit":
            break
        print(f"Demi: {run_agent(user_input)}\n")