from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import zipfile

from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from services.excel_analyzer import analyze_excel
from config import UPLOAD_DIR

router = APIRouter()

# 📊 Allowed formats
ALLOWED_TYPES = [".xlsx", ".xls"]


# -------------------------
# 📥 Upload Excel
# -------------------------
@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only Excel files (.xlsx, .xls) are allowed"
            )

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        file_id = str(uuid.uuid4())
        file_name = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 🔥 Analyze
        result = analyze_excel(file_path, UPLOAD_DIR)

        return {
            "success": True,
            "message": "Excel analyzed successfully",

            "total_rows": result.get("total_rows", 0),
            "total_cols": result.get("total_cols", 0),

            "insights": result.get("insights", []),
            "charts": result.get("charts", [])
        }

    except HTTPException:
        raise

    except Exception as e:
        print("🔥 EXCEL ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Excel processing failed: {str(e)}"
        )


# -------------------------
# 📦 Download ZIP (All Charts)
# -------------------------
@router.get("/download-zip")
def download_zip():
    try:
        zip_path = os.path.join(UPLOAD_DIR, "charts.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(UPLOAD_DIR):
                if file.endswith(".png"):
                    file_path = os.path.join(UPLOAD_DIR, file)
                    zipf.write(file_path, file)

        return {
            "success": True,
            "url": "/files/charts.zip"
        }

    except Exception as e:
        print("🔥 ZIP ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"ZIP creation failed: {str(e)}"
        )


# -------------------------
# 📄 Download PDF Report
# -------------------------
@router.get("/download-pdf")
def download_pdf():
    try:
        pdf_path = os.path.join(UPLOAD_DIR, "charts_report.pdf")

        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []

        # Title
        elements.append(Paragraph("Excel Analysis Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        # 🔥 Add charts
        for file in os.listdir(UPLOAD_DIR):
            if file.endswith(".png"):
                img_path = os.path.join(UPLOAD_DIR, file)

                elements.append(Paragraph(file, styles["Heading3"]))
                elements.append(Spacer(1, 10))

                elements.append(Image(img_path, width=450, height=250))
                elements.append(Spacer(1, 20))

        doc.build(elements)

        return {
            "success": True,
            "url": "/files/charts_report.pdf"
        }

    except Exception as e:
        print("🔥 PDF ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )