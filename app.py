# app.py
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from rag_engine import RAGEngine

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"

# 1. เปลี่ยนการโหลดข้อมูลเป็นไฟล์ใหม่ของนักโภชนาการ
@st.cache_resource
def load_rag():
    # ตรวจสอบว่าสร้างไฟล์ knowledge/nutrition_kb.txt ไว้แล้วตาม Step 2
    return RAGEngine("knowledge/nutrition_kb.txt")

rag = load_rag()

# 2. ปรับแต่งหน้าตา UI ใหม่
st.title("🥗 LeanBuddy AI")
st.caption("คุยกับ 'โค้ชปั้น' เรื่องแคลอรี เมนูสุขภาพ และการลดน้ำหนัก")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("วันนี้กินอะไรไป หรืออยากให้โค้ชช่วยเรื่องไหน?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # RAG: Search ข้อมูลจาก nutrition_kb.txt
    context_chunks = rag.search(prompt, top_k=3)
    context = "\n---\n".join(context_chunks)

    # 3. ปรับ System Instruction ให้เป็น "โค้ชปั้น"
    full_prompt = f"""คุณคือ 'โค้ชปั้น' ผู้ช่วยนักโภชนาการส่วนตัว (LeanBuddy AI) 
ตอบคำถามด้วยความสุภาพ ให้กำลังใจ และใช้ข้อมูลอ้างอิงจากด้านล่างนี้
ถ้าไม่พบข้อมูลที่เกี่ยวข้อง ให้พยายามตอบตามหลักการลดน้ำหนักทั่วไป (เช่น การคุมแคลอรี) 
แต่อย่ามโนตัวเลขแคลอรีที่ไม่มีหลักการ

ข้อมูลประกอบ (Knowledge Base):
{context}

คำถามจากลูกค้า: {prompt}
"""
    
    response = client.models.generate_content(model=MODEL, contents=full_prompt)
    answer = response.text

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)