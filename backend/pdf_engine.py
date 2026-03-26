from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

def generate_pdf_report(data, file_path):

    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("VoiceDocAI - Excel Analytics Report", title_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Dataset Info
    elements.append(Paragraph("Dataset Information", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    dataset_info = data.get("dataset_info", {})
    info_data = [
        ["Rows", dataset_info.get("rows", "")],
        ["Columns", dataset_info.get("columns", "")]
    ]

    table = Table(info_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 1, colors.grey)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # KPI Summary
    elements.append(Paragraph("KPI Summary", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    summary = data.get("summary", {})
    for col, stats in summary.items():
        elements.append(Paragraph(f"<b>{col}</b>", styles["Heading3"]))
        for key, value in stats.items():
            elements.append(Paragraph(f"{key}: {value}", normal_style))
        elements.append(Spacer(1, 0.2 * inch))

    # Missing Values
    elements.append(Paragraph("Missing Values", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    missing = data.get("missing_values", {})
    missing_data = [["Column", "Missing Count"]]
    for col, count in missing.items():
        missing_data.append([col, str(count)])

    table = Table(missing_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 1, colors.grey)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # Correlation Matrix
    correlation = data.get("correlation_matrix")
    if correlation:
        elements.append(Paragraph("Correlation Matrix", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        headers = [""] + list(correlation.keys())
        corr_table = [headers]

        for row_key, row_values in correlation.items():
            row = [row_key] + [str(v) for v in row_values.values()]
            corr_table.append(row)

        table = Table(corr_table)
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(table)

    doc.build(elements)