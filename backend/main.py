
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import routes
from routes import document, excel, audio, tts

# Create app
app = FastAPI(
    title="AI Analyzer API 🚀",
    description="RAG + Excel Analyzer + Audio AI + TTS (Ollama powered)",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://voicedocai-new.onrender.com",
        "https://your-vercel-project.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
BASE_DIR = "storage"

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Static file serving
app.mount(
    "/files",
    StaticFiles(directory=UPLOAD_DIR),
    name="files"
)

app.mount(
    "/audio-files",
    StaticFiles(directory=AUDIO_DIR),
    name="audio-files"
)

# Register routes
app.include_router(document.router, prefix="/doc", tags=["Document"])
app.include_router(excel.router, prefix="/excel", tags=["Excel"])
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(tts.router, prefix="/tts", tags=["TTS"])


# Root endpoint
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


# Health check
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
