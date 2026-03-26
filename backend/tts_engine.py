import os
import uuid
import subprocess
import threading
import time
import re

# ===================================================
# 🔊 PIPER CONFIGURATION
# ===================================================
PIPER_PATH = r"C:\Users\gowtham\Downloads\piper_windows_amd64\piper\piper.exe"
VOICE_MODEL = r"C:\Users\gowtham\Downloads\piper_windows_amd64\piper\en_US-ryan-medium.onnx"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "output_audio")

os.makedirs(AUDIO_DIR, exist_ok=True)

# 🔒 Prevent parallel TTS conflicts
tts_lock = threading.Lock()

# ===================================================
# 🔊 TEXT SANITIZATION (CRITICAL FOR WINDOWS)
# ===================================================
def sanitize_text(text: str) -> str:
    """
    Remove emojis & unsupported Unicode (fixes charmap error)
    """
    # Remove non-ASCII (emoji, symbols)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def clean_text(text: str) -> str:
    """
    Clean and limit text length
    """
    text = text.replace("\n", " ")
    text = sanitize_text(text)
    return text[:1800]  # limit long responses


# ===================================================
# 🔊 GENERATE VOICE (PRODUCTION SAFE)
# ===================================================
def generate_voice(text, filename=None):
    """
    Generate WAV audio using Piper TTS.
    Safe for Windows + background thread.
    """

    if not text or not text.strip():
        print("⚠️ No text provided for TTS")
        return None

    text = clean_text(text)

    if not text:
        print("⚠️ Text empty after sanitization")
        return None

    if filename is None:
        filename = f"{uuid.uuid4()}.wav"

    file_path = os.path.join(AUDIO_DIR, filename)

    try:
        with tts_lock:

            start_time = time.time()

            process = subprocess.Popen(
                [
                    PIPER_PATH,
                    "-m", VOICE_MODEL,
                    "--length-scale", "1.2",   # speech speed
                    "--noise-scale", "0.6",    # clarity
                    "-f", file_path
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )

            try:
                _, stderr = process.communicate(input=text, timeout=45)
            except subprocess.TimeoutExpired:
                process.kill()
                print("⏱ Piper timeout")
                return None

            generation_time = round(time.time() - start_time, 2)

            if process.returncode != 0:
                print("❌ Piper failed:", stderr)
                return None

            # Small wait to ensure file flush
            time.sleep(0.2)

            # Validate file
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1500:
                print(f"✅ Audio created ({generation_time}s):", file_path)
                return filename
            else:
                print("⚠️ Audio file invalid or too small")
                return None

    except Exception as e:
        print("❌ Piper Error:", e)
        return None