from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.vector_store import save_db, load_db
from services.llm_service import get_llm


# -------------------------
# 🔹 Split text into chunks
# -------------------------
def create_chunks(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=150
    )
    return splitter.split_text(text)


# -------------------------
# 🔹 Build vector DB
# -------------------------
def build_rag(text: str, db_path: str):
    chunks = create_chunks(text)

    if not chunks:
        raise ValueError("No content to build RAG")

    save_db(chunks, db_path)


# -------------------------
# 🔹 Detect user intent
# -------------------------
def detect_intent(query: str):
    q = query.lower()

    if any(k in q for k in ["summarize", "summary", "short"]):
        return "summary"

    elif any(k in q for k in ["question and answer", "q&a", "qa pairs"]):
        return "qa_pairs"

    elif any(k in q for k in ["generate questions", "only questions", "questions only"]):
        return "questions"

    else:
        return "normal"


# -------------------------
# 🔹 Format context safely
# -------------------------
def build_context(docs, max_chars=3000):
    context = ""
    for d in docs:
        if len(context) + len(d.page_content) > max_chars:
            break
        context += d.page_content + "\n\n"
    return context.strip()


# -------------------------
# 🔹 Main RAG logic
# -------------------------
def ask_rag(query: str, db_path: str):
    try:
        db = load_db(db_path)

        if db is None:
            raise ValueError("Vector DB not found")

        # 🔹 Retrieve relevant chunks
        docs = db.similarity_search(query, k=4)

        if not docs:
            return {
                "intent": "none",
                "answer": "No relevant information found.",
                "sources": []
            }

        context = build_context(docs)

        llm = get_llm()
        intent = detect_intent(query)

        # -------------------------
        # 🔥 Prompt Engineering
        # -------------------------
        if intent == "summary":
            prompt = f"""
You are an AI assistant.

Give a concise and clear summary (5–6 lines max).
Do NOT add extra information.

Content:
{context}
"""

        elif intent == "qa_pairs":
            prompt = f"""
Based ONLY on the content below, generate important Question & Answer pairs.

Rules:
- Minimum 5 Q&A
- Answers must be short
- No external knowledge

Content:
{context}
"""

        elif intent == "questions":
            prompt = f"""
Generate important questions from the content below.

Rules:
- Minimum 5 questions
- Do NOT include answers

Content:
{context}
"""

        else:
            prompt = f"""
You must answer ONLY from the given context.
If answer is not in context, say: "Not found in document".

Context:
{context}

Question:
{query}

Answer:
"""

        # 🔹 Call LLM
        response = llm.invoke(prompt)

        return {
            "intent": intent,
            "answer": response,
            "sources": [d.page_content[:200] for d in docs]
        }

    except Exception as e:
        return {
            "intent": "error",
            "answer": f"Error: {str(e)}",
            "sources": []
        }