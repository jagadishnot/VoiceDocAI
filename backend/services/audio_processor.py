# services/audio_processor.py

import torch
import whisper
from functools import lru_cache


# -------------------------
# 🔥 Detect Device (GPU / CPU)
# -------------------------
def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


# -------------------------
# 🔹 Load Whisper Model (Cached)
# -------------------------
@lru_cache(maxsize=1)
def get_whisper_model(model_name: str = "tiny"):
    device = get_device()

    print(f"🚀 Loading Whisper model ({model_name}) on {device}")

    model = whisper.load_model(model_name, device=device)

    return model


# -------------------------
# 🎧 Transcribe Audio
# -------------------------
def transcribe_audio(file_path: str, max_chars: int = 1500):
    try:
        device = get_device()
        model = get_whisper_model("tiny")  # ⚡ fastest

        print(f"🎧 Transcribing on {device}...")

        # 🔥 Optimized transcription
        result = model.transcribe(
            file_path,
            fp16=(device == "cuda"),   # GPU optimization
            verbose=False
        )

        transcript = result.get("text", "").strip()
        language = result.get("language", "unknown")

        # 🔥 Reduce size for LLM speed
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars]

        return {
            "success": True,
            "transcript": transcript,
            "language": language
        }

    except Exception as e:
        print("🔥 TRANSCRIPTION ERROR:", str(e))

        return {
            "success": False,
            "error": f"Transcription failed: {str(e)}"
        }