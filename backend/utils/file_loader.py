from pypdf import PdfReader
import docx

def load_pdf(path):
    reader = PdfReader(path)
    return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])

def load_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])