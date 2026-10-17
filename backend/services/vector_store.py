import os
from functools import lru_cache

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# -------------------------
# 🔹 Load embedding model (cached)
# -------------------------
@lru_cache(maxsize=1)
def get_embedding():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# -------------------------
# 🔹 Save vector DB
# -------------------------
def save_db(chunks, path):
    try:
        if not chunks:
            raise ValueError("No chunks to store")

        os.makedirs(path, exist_ok=True)

        embedding = get_embedding()

        db = FAISS.from_texts(chunks, embedding)
        db.save_local(path)

    except Exception as e:
        raise RuntimeError(f"Failed to save vector DB: {str(e)}")


# -------------------------
# 🔹 Load vector DB
# -------------------------
def load_db(path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError("Vector DB path does not exist")

        embedding = get_embedding()

        db = FAISS.load_local(
            path,
            embedding,
            allow_dangerous_deserialization=True  # required for FAISS
        )

        return db

    except Exception as e:
        raise RuntimeError(f"Failed to load vector DB: {str(e)}")