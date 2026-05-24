from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

app = FastAPI()


class ReplyRequest(BaseModel):
    message: str
    tone: str
    context: str
    mode: str


@app.get("/")
def root():
    return {
        "message":
            "Reply For Me API Running"
    }


@app.post("/generate-reply")
def generate_reply(data: ReplyRequest):

    if data.mode == "Tulis Ulang":

        task_instruction = f"""
        Tugas:
        Perbaiki dan tulis ulang pesan berikut agar lebih natural sesuai tone dan konteks.

        PENTING:
        - Jangan membalas pesan
        - Jangan menjawab pesan
        - Jangan membuat respon baru
        - Fokus memperbaiki kalimat user
        - Pertahankan maksud asli pesan
        - Buat lebih enak dibaca
        - Buat 3 versi berbeda

        Pesan user:
        {data.message}
        """

    elif data.mode == "Mode Ngeles":

        if data.context == "Boss":

            task_instruction = f"""
            Tugas:
            Buat 3 balasan ngeles yang sopan, aman, profesional, dan realistis untuk atasan kerja.

            PENTING:
            - Jangan terlalu lucu
            - Jangan bercanda berlebihan
            - Jangan terdengar tidak profesional
            - Jangan membuat alasan yang absurd
            - Tetap terdengar natural dan manusiawi
            - Harus aman digunakan untuk komunikasi kerja
            - Tetap singkat dan realistis

            Pesan:
            {data.message}
            """

        else:

            task_instruction = f"""
            Tugas:
            Buat 3 balasan dengan gaya ngeles yang lucu, realistis, halus, dan relatable.

            STYLE:
            - Terdengar natural
            - Jangan terlalu jahat
            - Jangan toxic
            - Jangan manipulatif berlebihan
            - Harus terasa seperti alasan manusia sehari-hari
            - Sedikit lucu boleh
            - Cocok dipakai di WhatsApp
            - Maksimal 1-2 kalimat

            Pesan:
            {data.message}
            """

    else:

        task_instruction = """
        Tugas:
        Buat 3 versi balasan berbeda.
        """

    prompt = f"""
    Kamu adalah AI assistant untuk membantu orang Indonesia membalas chat secara natural.

    STYLE:
    - Tulis seperti orang Indonesia asli saat chatting WhatsApp
    - Natural dan realistis
    - Santai dan manusiawi
    - Jangan terlalu formal
    - Jangan terdengar seperti AI atau customer service
    - Gunakan bahasa chat sehari-hari
    - Maksimal 1-2 kalimat
    - Setiap balasan harus terasa berbeda
    - Balasan harus cocok dipakai langsung di WhatsApp

    Konteks lawan bicara:
    {data.context}

    Tone balasan:
    {data.tone}

    Pesan:
    {data.message}

    {task_instruction}

    Format output:
    - langsung isi balasan saja
    - jangan gunakan nomor
    - jangan gunakan bullet point
    - pisahkan setiap balasan dengan baris baru
    """

    response = requests.post(
        url="https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization":
                f"Bearer {OPENAI_API_KEY}",
            "Content-Type":
                "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.9,
            "max_tokens": 120
        }
    )
    
    result = response.json()

    print("STATUS:")
    print(response.status_code)

    print("RESULT:")
    print(result)

    if response.status_code != 200:

        return {
            "success": False,
            "error": result
        }

    if "choices" not in result:

        return {
            "success": False,
            "error": result
        }

    text = result["choices"][0]["message"]["content"]

    replies = [
        line.strip("- ").strip()
        for line in text.split("\n")
        if line.strip()
    ]

    return {
        "replies": replies[:3]
    }