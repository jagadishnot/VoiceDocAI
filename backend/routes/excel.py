
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import zipfile

from reportlab.platypus import (
    SimpleDocTemplate,
    Image,
    Paragraph,
    Spacer,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from services.excel_analyzer import analyze_excel
from config import UPLOAD_DIR

router = APIRouter()

# Allowed Excel formats
ALLOWED_TYPES = {".xlsx", ".xls"}

# Maximum uploaded file size: 15 MB
MAX_FILE_SIZE = 15 * 1024 * 1024

# Read uploads in 1 MB chunks
CHUNK_SIZE = 1024 * 1024


# -------------------------
# Upload and analyze Excel
# -------------------------
@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    file_path = None

    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Please select an Excel file."
            )

        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only Excel files (.xlsx, .xls) are allowed."
            )

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Generate a unique, safe filename
        file_id = str(uuid.uuid4())
        safe_name = os.path.basename(file.filename)
        file_name = f"{file_id}_{safe_name}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        total_size = 0

        # Save the file incrementally to reduce upload memory usage
        with open(file_path, "wb") as output:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 15 MB upload limit."
                    )

                output.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        # Analyze the saved Excel file
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
        print("EXCEL ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Excel processing failed: {str(e)}"
        )

    finally:
        await file.close()


# -------------------------
# Download ZIP containing charts
# -------------------------
@router.get("/download-zip")
def download_zip():
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        zip_path = os.path.join(UPLOAD_DIR, "charts.zip")

        # Exclude the ZIP itself from the archive
        chart_files = [
            name
            for name in os.listdir(UPLOAD_DIR)
            if name.lower().endswith(".png")
            and os.path.isfile(os.path.join(UPLOAD_DIR, name))
        ]

        if not chart_files:
            raise HTTPException(
                status_code=404,
                detail="No charts available to download."
            )

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED
        ) as zipf:
            for name in chart_files:
                file_path = os.path.join(UPLOAD_DIR, name)
                zipf.write(file_path, arcname=name)

        return {
            "success": True,
            "url": "/files/charts.zip"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ZIP ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"ZIP creation failed: {str(e)}"
        )


# -------------------------
# Download PDF chart report
# -------------------------
@router.get("/download-pdf")
def download_pdf():
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        pdf_path = os.path.join(
            UPLOAD_DIR,
            "charts_report.pdf"
        )

        styles = getSampleStyleSheet()
        elements = []

        elements.append(
            Paragraph("Excel Analysis Report", styles["Title"])
        )
        elements.append(Spacer(1, 20))

        chart_files = [
            name
            for name in os.listdir(UPLOAD_DIR)
            if name.lower().endswith(".png")
            and os.path.isfile(os.path.join(UPLOAD_DIR, name))
        ]

        if not chart_files:
            raise HTTPException(
                status_code=404,
                detail="No charts available for the PDF report."
            )

        for name in chart_files:
            img_path = os.path.join(UPLOAD_DIR, name)

            elements.append(
                Paragraph(name, styles["Heading3"])
            )
            elements.append(Spacer(1, 10))

            # Preserve the chart's aspect ratio
            elements.append(
                Image(
                    img_path,
                    width=450,
                    height=250,
                    kind="proportional"
                )
            )
            elements.append(Spacer(1, 20))

        document = SimpleDocTemplate(
            pdf_path,
            pagesize=letter
        )
        document.build(elements)

        return {
            "success": True,
            "url": "/files/charts_report.pdf"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("PDF ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
