from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from rag_engine import process_document, stream_answer
from excel_engine import process_excel
from tts_engine import generate_voice
from pdf_engine import generate_pdf_report

import os
import uuid
import shutil
from threading import Thread

app = FastAPI(title="VoiceDoc AI", version="3.1.0")

# ===================================================
# 🔹 Enable CORS
# ===================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔐 Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================
# 🔹 Directory Setup
# ===================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "output_audio")
PDF_DIR = os.path.join(BASE_DIR, "output_pdf")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# ===================================================
# 🔹 Request Model
# ===================================================
class QuestionRequest(BaseModel):
    question: str


# ===================================================
# 🔹 Health Check
# ===================================================
@app.get("/")
def root():
    return {"status": "VoiceDoc AI Backend Running 🚀"}


# ===================================================
# 1️⃣ Upload Document (RAG)
# ===================================================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        success = process_document(file_path)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="File uploaded but no readable content found."
            )

        return {"message": "File processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# 2️⃣ Ask Question (🔥 STREAM + AUDIO MARKER)
# ===================================================
@app.post("/ask")
async def ask(query: QuestionRequest):

    question = query.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    filename = f"{uuid.uuid4()}.wav"
    full_text = ""

    def generate():
        nonlocal full_text

        # 🔥 Stream LLM tokens instantly
        for token in stream_answer(question):
            full_text += token
            yield token

        # 🔊 After streaming completes → generate audio in background
        if full_text.strip():
            Thread(
                target=generate_voice,
                args=(full_text, filename),
                daemon=True
            ).start()

            # 🔥 Send special marker so frontend knows filename
            yield f"\n[AUDIO_FILE]{filename}"

    return StreamingResponse(generate(), media_type="text/plain")


# ===================================================
# 3️⃣ Upload Excel (Advanced Analytics)
# ===================================================
@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".xlsx"):
            raise HTTPException(
                status_code=400,
                detail="Only .xlsx files are allowed"
            )

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_excel(file_path)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# 4️⃣ Export PDF Report
# ===================================================
@app.post("/export-pdf")
async def export_pdf(data: dict):
    try:
        unique_filename = f"{uuid.uuid4()}_analytics_report.pdf"
        file_path = os.path.join(PDF_DIR, unique_filename)

        generate_pdf_report(data, file_path)

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename="analytics_report.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# 5️⃣ Serve Audio (WAIT SAFE MODE)
# ===================================================
@app.get("/audio/{filename}")
def get_audio(filename: str):

    file_path = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(file_path) and os.path.getsize(file_path) > 1500:
        return FileResponse(
            path=file_path,
            media_type="audio/wav",
            filename=filename
        )

    return JSONResponse(
        status_code=202,
        content={"status": "processing"}
    )