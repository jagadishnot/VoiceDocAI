from services.llm_service import get_llm


def process_transcript(transcript: str, mode="summary", target_lang="English"):
    try:
        # -------------------------
        # 🔹 Validate input
        # -------------------------
        if not transcript or not transcript.strip():
            return {"success": False, "error": "Transcript is empty"}

        # 🔹 Normalize
        transcript = transcript.strip()
        mode = (mode or "").lower().strip()

        # 🔥 Limit size (important for speed)
        transcript = transcript[:1200]

        # -------------------------
        # 🧠 Use LOCAL LLM (mistral)
        # -------------------------
        llm = get_llm("mistral")

        # -------------------------
        # 🔥 Prompt Engineering
        # -------------------------
        if mode == "translate":
            # ⚡ shorter text for faster translation
            text = transcript[:500]

            prompt = f"""
Translate the following text into {target_lang}.
Return ONLY translated text.

{text}
"""

        elif mode == "summary":
            prompt = f"""
Summarize the following in 4–5 short lines:

{transcript}
"""

        elif mode == "conversation":
            prompt = f"""
Extract key discussion points.

Rules:
- Bullet points
- Short and clear

{transcript}
"""

        elif mode == "notes":
            prompt = f"""
Convert into clean study notes.

Rules:
- Bullet points
- Highlight important ideas
- Simple language

{transcript}
"""

        else:
            return {"success": False, "error": f"Invalid mode: {mode}"}

        # -------------------------
        # 🔹 Call LLM (with retry)
        # -------------------------
        for attempt in range(2):
            try:
                response = llm.invoke(prompt)

                if response is None:
                    raise ValueError("Empty response")

                if isinstance(response, dict):
                    output = response.get("content", "")
                else:
                    output = str(response)

                output = output.strip()

                if not output:
                    raise ValueError("Empty output")

                return {
                    "success": True,
                    "output": output
                }

            except Exception as retry_err:
                print(f"⚠️ Retry {attempt+1} failed:", retry_err)
                if attempt == 1:
                    raise retry_err

    except Exception as e:
        print("🔥 LLM AUDIO ERROR:", str(e))

        return {
            "success": False,
            "error": f"LLM processing failed: {str(e)}"
        }