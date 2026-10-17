# routes/document.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import uuid

from utils.file_loader import load_pdf, load_docx
from services.rag_pipeline import build_rag, ask_rag
from config import UPLOAD_DIR, VECTOR_DB_DIR

router = APIRouter()

# 📄 Allowed formats
ALLOWED_TYPES = [".pdf", ".docx"]

# 🔥 Limits
MAX_FILE_SIZE_MB = 20
MAX_TEXT_LENGTH = 20000


# -------------------------
# 📥 Upload Document
# -------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # 🔹 Validate file type
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported"
            )

        # 🔹 Read file (size check)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 20MB)"
            )

        # 🔹 Ensure folders exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)

        # 🔹 Create session
        session_id = str(uuid.uuid4())

        # 🔹 Save file
        file_name = f"{session_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(content)

        # 🔹 Extract text
        if ext == ".pdf":
            text = load_pdf(file_path)
        else:
            text = load_docx(file_path)

        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Document is empty or unreadable"
            )

        # 🔥 Limit text size (important for LLM)
        text = text[:MAX_TEXT_LENGTH]

        # 🔹 Build RAG
        db_path = os.path.join(VECTOR_DB_DIR, session_id)
        build_rag(text, db_path)

        return {
            "success": True,
            "session_id": session_id,
            "message": "Document processed successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("🔥 DOCUMENT UPLOAD ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )


# -------------------------
# 💬 Ask Question
# -------------------------
@router.post("/ask")
def ask(query: str = Form(...), session_id: str = Form(...)):
    try:
        # 🔹 Validate input
        if not query or not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query is empty"
            )

        db_path = os.path.join(VECTOR_DB_DIR, session_id)

        if not os.path.exists(db_path):
            raise HTTPException(
                status_code=404,
                detail="Session not found. Upload document first."
            )

        # 🔹 Ask RAG
        result = ask_rag(query.strip(), db_path)

        answer = result.get("answer", "").strip()

        if not answer:
            answer = "No relevant answer found."

        return {
            "success": True,
            "answer": answer,
            "sources": result.get("sources", []),
            "intent": result.get("intent", "normal")
        }

    except HTTPException:
        raise

    except Exception as e:
        print("🔥 DOCUMENT QUERY ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )