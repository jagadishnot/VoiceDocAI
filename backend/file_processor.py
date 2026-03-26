import os
import re
from pypdf import PdfReader
from docx import Document


# ==========================================
# 🔒 PERFORMANCE LIMITS
# ==========================================
MAX_PDF_PAGES = 40
MAX_TOTAL_CHARS = 80000


# ==========================================
# 🧹 ADVANCED TEXT CLEANING
# ==========================================
def clean_text(text: str) -> str:
    """
    Professional cleaning:
    - Remove multiple spaces
    - Fix broken words
    - Remove excessive newlines
    - Remove page numbers
    """

    # Remove page numbers like "Page 1"
    text = re.sub(r"Page\s*\d+", "", text, flags=re.IGNORECASE)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove strange unicode junk
    text = text.encode("utf-8", "ignore").decode("utf-8")

    return text.strip()


# ==========================================
# 📄 PDF EXTRACTION (PRO VERSION)
# ==========================================
def extract_pdf(file_path):
    try:
        reader = PdfReader(file_path)

        text = ""
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, MAX_PDF_PAGES)

        print(f"Reading {pages_to_read}/{total_pages} pages")

        for i in range(pages_to_read):
            page = reader.pages[i]
            page_text = page.extract_text()

            if page_text:
                text += "\n\n" + page_text

            if len(text) > MAX_TOTAL_CHARS:
                print("Reached character limit.")
                break

        text = clean_text(text)

        # If PDF is scanned (no text extracted)
        if len(text) < 100:
            print("Warning: PDF may be scanned (no readable text found).")

        print(f"Final extracted chars: {len(text)}")
        return text

    except Exception as e:
        print("PDF extraction error:", e)
        return ""


# ==========================================
# 📄 DOCX EXTRACTION (PRO VERSION)
# ==========================================
def extract_docx(file_path):
    try:
        doc = Document(file_path)

        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())

        text = "\n\n".join(paragraphs)
        text = text[:MAX_TOTAL_CHARS]
        text = clean_text(text)

        print(f"Extracted DOCX chars: {len(text)}")
        return text

    except Exception as e:
        print("DOCX extraction error:", e)
        return ""


# ==========================================
# 📄 TXT EXTRACTION (PRO VERSION)
# ==========================================
def extract_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        text = text[:MAX_TOTAL_CHARS]
        text = clean_text(text)

        print(f"Extracted TXT chars: {len(text)}")
        return text

    except Exception as e:
        print("TXT extraction error:", e)
        return ""


# ==========================================
# 🧠 METADATA EXTRACTION (NEW)
# ==========================================
def extract_metadata(file_path):
    metadata = {}

    try:
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            info = reader.metadata

            if info:
                metadata["title"] = str(info.title) if info.title else None
                metadata["author"] = str(info.author) if info.author else None

    except:
        pass

    return metadata


# ==========================================
# 📂 MAIN ENTRY FUNCTION
# ==========================================
def extract_text(file_path):

    if not os.path.exists(file_path):
        print("File not found.")
        return ""

    file_path = file_path.lower()

    # -------------------------
    # PDF
    # -------------------------
    if file_path.endswith(".pdf"):
        text = extract_pdf(file_path)

    # -------------------------
    # DOCX
    # -------------------------
    elif file_path.endswith(".docx"):
        text = extract_docx(file_path)

    # -------------------------
    # TXT
    # -------------------------
    elif file_path.endswith(".txt"):
        text = extract_txt(file_path)

    else:
        print("Unsupported file format.")
        return ""

    return text