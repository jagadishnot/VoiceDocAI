# routes/tts.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gtts import gTTS
import uuid
import os
import hashlib

router = APIRouter()

# 🔹 Config (MATCH main.py)
AUDIO_DIR = os.path.join("storage", "audio_outputs")
os.makedirs(AUDIO_DIR, exist_ok=True)

# 🔥 Limits
MAX_TEXT_LENGTH = 1000


# -------------------------
# 📦 Request Model
# -------------------------
class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    slow: bool = False


# -------------------------
# 🔑 Generate Hash (for caching)
# -------------------------
def generate_hash(text, lang, slow):
    key = f"{text}_{lang}_{slow}"
    return hashlib.md5(key.encode()).hexdigest()


# -------------------------
# 🔊 Text to Speech
# -------------------------
@router.post("/speak")
def text_to_speech(req: TTSRequest):
    try:
        # 🔹 Validate input
        if not req.text or not req.text.strip():
            raise HTTPException(status_code=400, detail="Text is empty")

        text = req.text.strip()

        # 🔥 Limit size
        text = text[:MAX_TEXT_LENGTH]

        # 🔹 Generate cache key
        file_hash = generate_hash(text, req.language, req.slow)
        filename = f"{file_hash}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        # 🔥 CACHE: if exists, reuse
        if os.path.exists(filepath):
            return {
                "success": True,
                "cached": True,
                "url": f"/audio-files/{filename}"
            }

        # 🔊 Generate TTS
        try:
            tts = gTTS(
                text=text,
                lang=req.language,
                slow=req.slow
            )
            tts.save(filepath)

        except Exception:
            # 🔥 Fallback to English if language fails
            tts = gTTS(text=text, lang="en", slow=req.slow)
            tts.save(filepath)

        return {
            "success": True,
            "cached": False,
            "message": "Audio generated",
            "url": f"/audio-files/{filename}",
            "filename": filename
        }

    except HTTPException:
        raise

    except Exception as e:
        print("🔥 TTS ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )