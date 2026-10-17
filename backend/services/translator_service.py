# services/translator_service.py

import requests


def translate_text(text: str, target_lang: str = "en"):
    try:
        if not text or not text.strip():
            return {"success": False, "error": "Empty text"}

        # 🔥 Use more stable public endpoint
        url = "https://translate.argosopentech.com/translate"

        payload = {
            "q": text[:1000],   # 🔥 limit size for stability
            "source": "auto",
            "target": target_lang,
            "format": "text"
        }

        response = requests.post(url, json=payload, timeout=15)

        # -------------------------
        # 🔹 Check HTTP status
        # -------------------------
        if response.status_code != 200:
            print("❌ STATUS:", response.status_code)
            print("❌ RESPONSE:", response.text)
            return {
                "success": False,
                "error": f"API error: {response.status_code}"
            }

        # -------------------------
        # 🔹 Safe JSON parsing
        # -------------------------
        try:
            data = response.json()
        except Exception:
            print("❌ INVALID JSON RESPONSE:", response.text)
            return {
                "success": False,
                "error": "Invalid API response"
            }

        translated = data.get("translatedText")

        if not translated:
            print("❌ EMPTY TRANSLATION:", data)
            return {
                "success": False,
                "error": "No translation returned"
            }

        return {
            "success": True,
            "translated_text": translated
        }

    except requests.exceptions.Timeout:
        print("⏳ Translation timeout")
        return {"success": False, "error": "Translation timeout"}

    except requests.exceptions.ConnectionError:
        print("🌐 Connection error")
        return {"success": False, "error": "Connection error"}

    except Exception as e:
        print("🔥 TRANSLATION ERROR:", str(e))
        return {
            "success": False,
            "error": str(e)
        }