import os
from functools import lru_cache
from langchain_ollama import OllamaLLM

# 🔹 Default config (override via env if needed)
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")   # 🔥 faster default
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", 0.2))
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", 120))


# -------------------------
# 🤖 Load LLM (cached per model)
# -------------------------
@lru_cache(maxsize=3)
def get_llm(model: str = None):
    model = model or DEFAULT_MODEL

    try:
        return OllamaLLM(
            model=model,
            base_url=BASE_URL,
            temperature=TEMPERATURE,
            request_timeout=TIMEOUT
        )
    except Exception as e:
        raise RuntimeError(f"LLM init failed ({model}): {str(e)}")


# -------------------------
# ⚡ Safe generation helper
# -------------------------
def generate_response(prompt: str, model: str = None, retries: int = 2):
    try:
        if not prompt or not prompt.strip():
            return "Error: Empty prompt"

        # 🔥 Trim prompt (avoid overload)
        prompt = prompt.strip()[:2000]

        llm = get_llm(model)

        for attempt in range(retries + 1):
            try:
                response = llm.invoke(prompt)

                # 🔥 Normalize response
                if response is None:
                    raise ValueError("Empty response from LLM")

                if isinstance(response, dict):
                    output = response.get("content", "")
                else:
                    output = str(response)

                output = output.strip()

                if not output:
                    raise ValueError("LLM returned empty output")

                return output

            except Exception as inner_err:
                print(f"⚠️ Retry {attempt+1} failed:", inner_err)
                if attempt == retries:
                    raise inner_err

    except Exception as e:
        print("🔥 LLM ERROR:", e)
        return f"Error generating response: {str(e)}"