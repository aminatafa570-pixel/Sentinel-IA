from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def build_investigation_pdf(rows, filters_summary):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.0 * cm,
        leftMargin=1.0 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    styles = getSampleStyleSheet()

    content = [
        Paragraph(
            "Sentinel IA - Rapport d'enquete",
            styles["Title"],
        ),
        Spacer(1, 0.3 * cm),
        Paragraph(filters_summary, styles["Normal"]),
        Spacer(1, 0.3 * cm),
        Paragraph(
            f"Nombre d'evenements analyses : {len(rows)}",
            styles["Normal"],
        ),
        Spacer(1, 0.5 * cm),
    ]

    data = [[
        "Date / heure",
        "Utilisateur",
        "IP",
        "Appareil",
        "Score",
        "Decision",
        "Incident / Analyste",
    ]]

    for row in rows:
        data.append([
            Paragraph(str(row["Date / heure"]), styles["BodyText"]),
            Paragraph(str(row["Utilisateur"]), styles["BodyText"]),
            Paragraph(str(row["IP"]), styles["BodyText"]),
            Paragraph(str(row["Appareil"]), styles["BodyText"]),
            Paragraph(str(row["Score"]), styles["BodyText"]),
            Paragraph(str(row["Décision"]), styles["BodyText"]),
            Paragraph(
                f"{row['Incident']}<br/>{row['Analyste']}",
                styles["BodyText"],
            ),
        ])

    table = Table(
        data,
        colWidths=[
            3.3 * cm,
            2.7 * cm,
            3.1 * cm,
            4.0 * cm,
            1.5 * cm,
            3.0 * cm,
            5.0 * cm,
        ],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.HexColor("#F8FAFC"),
            colors.white,
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    content.append(table)
    document.build(content)

    buffer.seek(0)
    return buffer.getvalue()