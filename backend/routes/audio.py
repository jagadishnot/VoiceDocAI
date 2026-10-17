from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import uuid

from services.audio_processor import transcribe_audio
from services.llm_audio import process_transcript
from config import UPLOAD_DIR

# ✅ Router
router = APIRouter()

# 🎧 Allowed audio types
ALLOWED_TYPES = [".mp3", ".wav", ".m4a"]
MAX_FILE_SIZE_MB = 25


# -------------------------
# 📥 Upload Audio
# -------------------------
@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported audio format (mp3/wav/m4a only)"
            )

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        content = await file.read()

        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 25MB)"
            )

        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as f:
            f.write(content)

        # 🔹 Transcribe
        result = transcribe_audio(file_path)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Transcription failed")
            )

        transcript = result.get("transcript", "").strip()

        if not transcript:
            raise HTTPException(
                status_code=500,
                detail="Empty transcript generated"
            )

        return {
            "success": True,
            "transcript": transcript,
            "language": result.get("language", "unknown")
        }

    except HTTPException:
        raise
    except Exception as e:
        print("🔥 AUDIO UPLOAD ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail="Audio processing failed"
        )


# -------------------------
# 🔄 Process Transcript
# -------------------------
class ProcessRequest(BaseModel):
    transcript: str
    mode: str
    language: str = "English"


@router.post("/process")
def process_text(req: ProcessRequest):
    try:
        if not req.transcript or not req.transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcript is empty"
            )

        mode = req.mode.lower().strip()

        # 🌍 Normalize language
        LANG_MAP = {
            "english": "English",
            "tamil": "Tamil",
            "hindi": "Hindi",
            "french": "French"
        }

        language = LANG_MAP.get(req.language.lower(), "English")

        # 🔥 Debug logs (keep during dev)
        print("\n====== AUDIO PROCESS DEBUG ======")
        print("MODE:", mode)
        print("LANG:", language)
        print("TRANSCRIPT SAMPLE:", req.transcript[:100])
        print("================================\n")

        # 🔹 Call processing service
        result = process_transcript(
            transcript=req.transcript,
            mode=mode,
            target_lang=language
        )

        if not result.get("success"):
            print("❌ PROCESS ERROR:", result.get("error"))
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Processing failed")
            )

        output = result.get("output", "").strip()

        if not output:
            raise HTTPException(
                status_code=500,
                detail="Empty output from processing"
            )

        return {
            "success": True,
            "mode": mode,
            "output": output
        }

    except HTTPException:
        raise
    except Exception as e:
        print("🔥 AUDIO PROCESS ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail="Processing failed"
        )