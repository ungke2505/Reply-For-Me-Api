from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
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

    else:

        task_instruction = """
        Tugas:
        Buat 3 versi balasan berbeda.
        """

    prompt = f"""
    Kamu adalah AI assistant untuk membantu orang Indonesia membalas chat secara natural.

    STYLE WAJIB:
    - Terdengar seperti manusia
    - Singkat dan jelas
    - Jangan terlalu formal
    - Jangan terlalu kaku
    - Jangan seperti customer service
    - Jangan seperti AI
    - Hindari bahasa baku berlebihan
    - Maksimal 1-2 kalimat
    - Balasan harus realistis dipakai di WhatsApp

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
        url=
            "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":
                "application/json",
        },
        json={
            "model":
                "openai/gpt-oss-120b:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    )

    result = response.json()

    print(response.status_code)
    print(result)

    if "choices" not in result:
        return {
            "success": False,
            "provider_response": result
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