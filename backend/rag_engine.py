import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
from file_processor import extract_text

# =====================================================
# 🔥 EMBEDDING MODEL (Fast + Stable)
# =====================================================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatIP(dimension)

documents = []
document_uploaded = False
document_summary = ""


# =====================================================
# 📄 PROCESS DOCUMENT
# =====================================================
def process_document(file_path):
    global documents, document_uploaded, document_summary, index

    text = extract_text(file_path)

    if not text or not text.strip():
        return False

    documents.clear()
    index.reset()

    text = text[:80000]  # allow slightly bigger context

    document_summary = text[:4000]  # for describe/summary

    chunk_size = 600
    overlap = 120

    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size].strip()
        if len(chunk) > 150:
            chunks.append(chunk)

    chunks = chunks[:120]

    documents.extend(chunks)

    embeddings = embed_model.encode(
        chunks,
        normalize_embeddings=True,
        batch_size=16,
        show_progress_bar=False
    )

    index.add(np.array(embeddings, dtype="float32"))

    document_uploaded = True
    return True


# =====================================================
# 🧠 STREAM LLM
# =====================================================
def stream_llm(model_name, prompt):

    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.15,
            "num_predict": 300
        },
        stream=True
    )

    for chunk in response:
        token = chunk.get("message", {}).get("content", "")
        if token:
            yield token


# =====================================================
# 🎯 SMART INTENT DETECTION
# =====================================================
def detect_intent(question):
    q = question.lower()

    if any(k in q for k in ["describe", "overview", "what is inside", "about this file","explain shortly",]):
        return "describe"

    if any(k in q for k in ["summarize", "summary"]):
        return "summary"

    if any(k in q for k in ["generate question", "create question", "make questions"]):
        return "question_generation"

    if any(k in q for k in ["short", "brief", "in short","give short about thre file"]):
        return "short_answer"

    return "normal"


# =====================================================
# 🔍 RETRIEVE CONTEXT (WITH CONFIDENCE CHECK)
# =====================================================
def retrieve_context(question, k=5, threshold=0.35):

    query_vector = embed_model.encode(
        [question],
        normalize_embeddings=True
    )

    D, I = index.search(np.array(query_vector, dtype="float32"), k=k)

    relevant = []
    for score, idx in zip(D[0], I[0]):
        if score > threshold:
            relevant.append(documents[idx])

    return relevant


# =====================================================
# 🚀 STREAM ANSWER (FINAL PRO ENGINE)
# =====================================================
def stream_answer(question):

    global document_uploaded, document_summary

    question = question.strip()

    # =================================================
    # 1️⃣ NO DOCUMENT → PURE CHAT MODE
    # =================================================
    if not document_uploaded:

        prompt = f"""
You are a helpful AI assistant.

Answer clearly and professionally in short.

Question:
{question}
"""
        yield from stream_llm("phi3:mini", prompt)
        return

    intent = detect_intent(question)

    # =================================================
    # 2️⃣ DESCRIBE MODE (Structured)
    # =================================================
    if intent == "describe":

        prompt = f"""
You are analyzing an uploaded document.

Provide a professional structured explanation:

📄 Document Overview:
(Short introduction)

🧠 Main Topics:
(Bullet points)

📌 Key Concepts:
(Short explanation each)

🎯 Purpose:
(Why document exists)

🏁 Conclusion:
(Short closing)

Use only document content.

Document:
{document_summary}
"""
        yield from stream_llm("phi3", prompt)
        return

    # =================================================
    # 3️⃣ SUMMARY MODE
    # =================================================
    if intent == "summary":

        prompt = f"""
Provide a concise but complete structured summary.

Document:
{document_summary}
"""
        yield from stream_llm("phi3", prompt)
        return

    # =================================================
    # 4️⃣ QUESTION GENERATION MODE
    # =================================================
    if intent == "question_generation":

        context = "\n\n".join(documents[:8])

        prompt = f"""
Generate 10 meaningful study questions from this document.

Document:
{context}
"""
        yield from stream_llm("phi3", prompt)
        return

    # =================================================
    # 5️⃣ RETRIEVE DOCUMENT CONTEXT
    # =================================================
    context_chunks = retrieve_context(question)

    # =================================================
    # 6️⃣ IF QUESTION NOT RELATED → FALLBACK CHAT
    # =================================================
    if not context_chunks:

        prompt = f"""
The question does not seem directly related to the uploaded document.

Answer normally as a helpful assistant.

Question:
{question}
"""
        yield from stream_llm("phi3:mini", prompt)
        return

    context = "\n\n".join(context_chunks[:4])

    # =================================================
    # 7️⃣ NORMAL PROFESSIONAL RAG ANSWER
    # =================================================
    prompt = f"""
You are answering using ONLY the uploaded document.

Follow this format:

🔹 Direct Answer:
(Clear answer)

🔹 Explanation:
(Explain using document context)

🔹 Key Points:
- Bullet points

If answer is not clearly found, say:
"The answer is not available in the uploaded document."

Document Context:
{context}

User Question:
{question}
"""

    yield from stream_llm("phi3", prompt)