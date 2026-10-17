from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# 🔹 Import routes
from routes import document, excel, audio, tts

# ==========================
# 🚀 CREATE APP
# ==========================
app = FastAPI(
    title="AI Analyzer API 🚀",
    description="RAG + Excel Analyzer + Audio AI + TTS (Ollama powered)",
    version="2.0.0"
)

# ==========================
# 🌐 CORS (Frontend Support)
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⚠️ change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# 📁 DIRECTORY SETUP
# ==========================
BASE_DIR = "storage"

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# ==========================
# 📂 STATIC FILE SERVING
# ==========================

# 📊 Charts / Files
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# 🔊 TTS Audio
app.mount("/audio-files", StaticFiles(directory=AUDIO_DIR), name="audio-files")

# ==========================
# 📄 ROUTES
# ==========================
app.include_router(document.router, prefix="/doc", tags=["Document"])
app.include_router(excel.router, prefix="/excel", tags=["Excel"])
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(tts.router, prefix="/tts", tags=["TTS"])

# ==========================
# 🏠 ROOT
# ==========================
@app.get("/")
def home():
    return {
        "status": "AI Analyzer Running 🚀",
        "version": "2.0",
        "features": [
            "📄 Document RAG Q&A",
            "📊 Excel Data Analyzer",
            "🎧 Audio Transcription + AI",
            "🔊 Text-to-Speech"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "document": "/doc",
            "excel": "/excel",
            "audio": "/audio",
            "tts": "/tts",
            "files": "/files/<filename>",
            "audio_files": "/audio-files/<filename>"
        }
    }

# ==========================
# 💚 HEALTH CHECK
# ==========================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "services": {
            "document": True,
            "excel": True,
            "audio": True,
            "tts": True
        }
    }