from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from models.audit_log import AuditLog
from reports.audit_report import build_weekly_audit_pdf


st.set_page_config(
    page_title="Audit Log Sentinel IA",
    page_icon="📜",
    layout="wide",
)

st.title("📜 Audit Log")
st.caption(
    "Traçabilité des décisions Sentinel IA et des actions analystes."
)

today = datetime.now(timezone.utc).date()

date_left, date_right = st.columns(2)

start_date = date_left.date_input(
    "Début du rapport",
    value=today - timedelta(days=6),
)

end_date = date_right.date_input(
    "Fin du rapport",
    value=today,
)

if start_date > end_date:
    st.error("La date de début doit être antérieure à la date de fin.")
    st.stop()

session = SessionLocal()

try:
    logs = (
        session.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(500)
        .all()
    )

    if not logs:
        st.info(
            "Aucune activité enregistrée. Lance une simulation "
            "ou applique une action dans un incident."
        )
    else:
        weekly_logs = [
            log
            for log in logs
            if log.timestamp
            and start_date <= log.timestamp.date() <= end_date
        ]

        pdf_data = build_weekly_audit_pdf(
            weekly_logs,
            start_date,
            end_date,
        )

        st.download_button(
            "Télécharger le rapport PDF",
            data=pdf_data,
            file_name=(
                f"sentinel_audit_{start_date}_au_{end_date}.pdf"
            ),
            mime="application/pdf",
            type="primary",
        )

        st.divider()

        rows = [
            {
                "Date / heure": log.timestamp,
                "Acteur": log.actor,
                "Action": log.action,
                "Cible": f"{log.target_type} #{log.target_id}",
                "Détails": log.details,
            }
            for log in logs
        ]

        dataframe = pd.DataFrame(rows)

        col1, col2 = st.columns(2)

        actor_filter = col1.multiselect(
            "Acteurs",
            sorted(dataframe["Acteur"].dropna().unique()),
        )

        action_filter = col2.multiselect(
            "Actions",
            sorted(dataframe["Action"].dropna().unique()),
        )

        if actor_filter:
            dataframe = dataframe[
                dataframe["Acteur"].isin(actor_filter)
            ]

        if action_filter:
            dataframe = dataframe[
                dataframe["Action"].isin(action_filter)
            ]

        st.metric("Actions enregistrées", len(dataframe))

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

finally:
    session.close()