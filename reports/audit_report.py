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


def build_weekly_audit_pdf(logs, start_date, end_date):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()
    content = [
        Paragraph("Sentinel IA - Rapport hebdomadaire d'audit", styles["Title"]),
        Spacer(1, 0.3 * cm),
        Paragraph(
            f"Periode : {start_date.strftime('%d/%m/%Y')} "
            f"au {end_date.strftime('%d/%m/%Y')}",
            styles["Normal"],
        ),
        Spacer(1, 0.5 * cm),
        Paragraph(f"Nombre d'actions : {len(logs)}", styles["Normal"]),
        Spacer(1, 0.4 * cm),
    ]

    table_data = [[
        "Date / heure",
        "Acteur",
        "Action",
        "Cible",
        "Details",
    ]]

    for log in logs:
        timestamp = (
            log.timestamp.strftime("%d/%m/%Y %H:%M UTC")
            if log.timestamp
            else "Non disponible"
        )

        table_data.append([
            Paragraph(timestamp, styles["BodyText"]),
            Paragraph(str(log.actor or ""), styles["BodyText"]),
            Paragraph(str(log.action or ""), styles["BodyText"]),
            Paragraph(
                f"{log.target_type or ''} #{log.target_id or ''}",
                styles["BodyText"],
            ),
            Paragraph(str(log.details or ""), styles["BodyText"]),
        ])

    table = Table(
        table_data,
        colWidths=[3.2 * cm, 3.2 * cm, 4.2 * cm, 3.0 * cm, 11.0 * cm],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.HexColor("#F8FAFC"),
            colors.white,
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    content.append(table)
    document.build(content)

    buffer.seek(0)
    return buffer.getvalue()