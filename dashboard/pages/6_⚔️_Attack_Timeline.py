from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from database.database import SessionLocal
from models.alert import Alert
from models.incident import Incident
from models.event import Event
from reports.investigation_report import build_investigation_pdf


st.set_page_config(
    page_title="Attack Timeline",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ Attack Timeline")
st.caption(
    "Recherchez, analysez et exportez l'historique complet d'une enquête."
)

session = SessionLocal()

try:
    events = (
        session.query(Event)
        .order_by(Event.id.desc())
        .limit(500)
        .all()
    )

    alerts = session.query(Alert).all()
    incidents = session.query(Incident).all()

    if not events:
        st.info("Aucun événement enregistré. Lance une simulation.")
        st.stop()

    alert_by_event = {
        alert.event_id: alert
        for alert in alerts
        if alert.event_id
    }

    incident_by_alert = {
        incident.alert_id: incident
        for incident in incidents
    }

    today = datetime.now(timezone.utc).date()

    st.subheader("Filtres d'enquête")

    col1, col2, col3 = st.columns(3)

    start_date = col1.date_input(
        "Date de début",
        value=today - timedelta(days=30),
    )

    end_date = col2.date_input(
        "Date de fin",
        value=today,
    )

    selected_users = col3.multiselect(
        "Utilisateurs",
        sorted({event.user for event in events if event.user}),
    )

    col4, col5, col6 = st.columns(3)

    ip_query = col4.text_input("Adresse IP")
    device_query = col5.text_input("Appareil")
    selected_decisions = col6.multiselect(
        "Décisions Sentinel IA",
        sorted({
            event.security_action or "UNKNOWN"
            for event in events
        }),
    )

    analysts = sorted({
        incident.assigned_to
        for incident in incidents
        if incident.assigned_to
    })

    selected_analysts = st.multiselect(
        "Analyste responsable",
        analysts,
    )

    if start_date > end_date:
        st.error("La date de début doit être antérieure à la date de fin.")
        st.stop()

    filtered_events = []

    for event in events:
        event_date = event.timestamp.date() if event.timestamp else None

        # Les anciens événements sans date restent consultables,
        # mais ne sont pas inclus dans une recherche par période.
        if not event_date or not (start_date <= event_date <= end_date):
            continue

        alert = alert_by_event.get(event.id)
        incident = (
            incident_by_alert.get(alert.id)
            if alert
            else None
        )

        analyst = (
            incident.assigned_to
            if incident and incident.assigned_to
            else "Non attribué"
        )

        if selected_users and event.user not in selected_users:
            continue

        if ip_query and ip_query.lower() not in (
            event.ip_address or ""
        ).lower():
            continue

        if device_query and device_query.lower() not in (
            event.device or ""
        ).lower():
            continue

        if (
            selected_decisions
            and (event.security_action or "UNKNOWN")
            not in selected_decisions
        ):
            continue

        if selected_analysts and analyst not in selected_analysts:
            continue

        filtered_events.append(
            (event, alert, incident, analyst)
        )

    rows = []

    for event, alert, incident, analyst in filtered_events:
        timestamp = (
            event.timestamp.strftime("%d/%m/%Y %H:%M UTC")
            if event.timestamp
            else "Indisponible"
        )

        rows.append({
            "Date / heure": timestamp,
            "Utilisateur": event.user or "UNKNOWN",
            "IP": event.ip_address or "UNKNOWN",
            "Appareil": event.device or "UNKNOWN",
            "Pays": event.location or "UNKNOWN",
            "Action": event.action or "UNKNOWN",
            "Score": f"{event.risk_score or 0}/100",
            "Décision": event.security_action or "UNKNOWN",
            "Niveau": event.risk_level or "UNKNOWN",
            "Raisons": event.risk_reasons or "Non disponible",
            "Incident": (
                f"#{incident.id} · {incident.status}"
                if incident
                else "Aucun incident"
            ),
            "Analyste": analyst,
        })

    dataframe = pd.DataFrame(rows)

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Événements trouvés", len(rows))
    metric_2.metric(
        "Incidents associés",
        sum(1 for row in rows if row["Incident"] != "Aucun incident"),
    )
    metric_3.metric(
        "Blocages définitifs",
        sum(1 for row in rows if row["Décision"] == "BLOCKED"),
    )

    filters_summary = (
        f"Période : {start_date.strftime('%d/%m/%Y')} "
        f"au {end_date.strftime('%d/%m/%Y')}<br/>"
        f"Utilisateurs : {', '.join(selected_users) or 'Tous'}<br/>"
        f"IP : {ip_query or 'Toutes'} · "
        f"Appareil : {device_query or 'Tous'}"
    )

    pdf_data = build_investigation_pdf(
        rows,
        filters_summary,
    )

    st.download_button(
        "Télécharger le rapport d'enquête PDF",
        data=pdf_data,
        file_name=(
            f"sentinel_enquete_{start_date}_au_{end_date}.pdf"
        ),
        mime="application/pdf",
        type="primary",
    )

    st.divider()
    st.subheader("Résultats de l'enquête")

    if dataframe.empty:
        st.warning("Aucun événement ne correspond à ces filtres.")
    else:
        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.subheader("Chronologie détaillée")

        for event, alert, incident, analyst in reversed(filtered_events):
            icon = {
                "ALLOWED": "🟢",
                "MFA_REQUIRED": "🟡",
                "TEMP_BLOCK": "🟠",
                "BLOCKED": "🔴",
            }.get(event.security_action, "⚪")

            timestamp = (
                event.timestamp.strftime("%d/%m/%Y à %H:%M UTC")
                if event.timestamp
                else "Date indisponible"
            )

            with st.container(border=True):
                st.write(
                    f"{icon} **{timestamp}** · "
                    f"{event.user} · "
                    f"{event.security_action or 'UNKNOWN'}"
                )

                st.write(
                    f"IP : {event.ip_address or 'UNKNOWN'} · "
                    f"Appareil : {event.device or 'UNKNOWN'} · "
                    f"Pays : {event.location or 'UNKNOWN'}"
                )

                st.write(
                    f"Score : {event.risk_score or 0}/100 · "
                    f"Raisons : {event.risk_reasons or 'Non disponible'}"
                )

                if incident:
                    st.info(
                        f"Incident #{incident.id} · "
                        f"Statut : {incident.status} · "
                        f"Analyste : {analyst}"
                    )

finally:
    session.close()