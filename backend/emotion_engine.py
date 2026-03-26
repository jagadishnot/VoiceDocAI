import ollama
import re
import hashlib
from functools import lru_cache

# ==========================================
# 🎯 CONFIG
# ==========================================
MODEL_NAME = "phi3:mini"
VALID_EMOTIONS = {"happy", "serious", "neutral", "excited", "sad"}
MAX_TEXT_LENGTH = 1000


# ==========================================
# 🧹 CLEAN TEXT
# ==========================================
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text[:MAX_TEXT_LENGTH]


# ==========================================
# 🔎 FALLBACK KEYWORD CLASSIFIER
# (Instant rule-based backup)
# ==========================================
def keyword_fallback(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["great", "awesome", "amazing", "love"]):
        return "happy"

    if any(word in text for word in ["wow", "incredible", "fantastic"]):
        return "excited"

    if any(word in text for word in ["sad", "unfortunately", "sorry"]):
        return "sad"

    if any(word in text for word in ["important", "critical", "must", "required"]):
        return "serious"

    return "neutral"


# ==========================================
# 🤖 LLM EMOTION DETECTION
# ==========================================
@lru_cache(maxsize=200)
def detect_emotion(text: str) -> str:
    """
    Detect emotion using LLM with strict parsing and fallback safety.
    """

    text = clean_text(text)

    if not text:
        return "neutral"

    prompt = f"""
You are an emotion classification system.

Classify the overall emotion of the following text.

Return ONLY one word from this list:
happy
serious
neutral
excited
sad

Do not explain.

Text:
{text}
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0,
                "num_predict": 5
            }
        )

        raw_output = response.get("message", {}).get("content", "").strip().lower()

        # Extract first valid word
        for word in VALID_EMOTIONS:
            if word in raw_output:
                return word

        # If LLM gives unexpected output → fallback
        return keyword_fallback(text)

    except Exception as e:
        print("Emotion detection error:", e)
        return keyword_fallback(text)