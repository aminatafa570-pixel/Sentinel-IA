from datetime import datetime, timezone

import streamlit as st

from database.database import SessionLocal
from models.alert import Alert
from models.incident import Incident
from security.response_engine import apply_response_action


st.set_page_config(
    page_title="Incident Response Center",
    page_icon="🧩",
    layout="wide",
)

st.title("🧩 Incident Response Center")
st.caption(
    "Créez, attribuez et suivez les incidents de sécurité Sentinel IA."
)

STATUS_OPTIONS = [
    "NEW",
    "INVESTIGATING",
    "CONTAINED",
    "RESOLVED",
    "CLOSED",
]

ANALYST_OPTIONS = [
    "Unassigned",
    "SOC Analyst - Marie",
    "SOC Analyst - Ahmed",
    "Security Lead - John",
]

RESPONSE_ACTIONS = [
    ("Lever le blocage", "LIFT_BLOCK"),
    ("Exiger MFA", "REQUIRE_MFA"),
    ("Maintenir le blocage", "MAINTAIN_TEMP_BLOCK"),
    ("Bloquer définitivement", "PERMANENT_BLOCK"),
    ("Révoquer les sessions", "REVOKE_SESSIONS"),
]


session = SessionLocal()

try:
    alerts = session.query(Alert).order_by(Alert.id.desc()).all()

    incidents = (
        session.query(Incident)
        .order_by(Incident.created_at.desc())
        .all()
    )

    open_incidents = [
        incident
        for incident in incidents
        if incident.status not in {"RESOLVED", "CLOSED"}
    ]

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Incidents ouverts", len(open_incidents))
    metric_2.metric(
        "En investigation",
        sum(
            incident.status == "INVESTIGATING"
            for incident in incidents
        ),
    )
    metric_3.metric(
        "Résolus / fermés",
        sum(
            incident.status in {"RESOLVED", "CLOSED"}
            for incident in incidents
        ),
    )

    st.divider()
    st.subheader("Créer un incident")

    if not alerts:
        st.info("Crée d’abord une alerte via le simulateur.")
    else:
        alert_options = {
            (
                f"#{alert.id} · {alert.level} · "
                f"{alert.user} · score {alert.score}/100"
            ): alert
            for alert in alerts
        }

        selected_label = st.selectbox(
            "Alerte à traiter",
            list(alert_options.keys()),
        )
        selected_alert = alert_options[selected_label]

        with st.form("create_incident"):
            default_title = (
                f"Investigation Sentinel · {selected_alert.user} "
                f"· alerte #{selected_alert.id}"
            )

            title = st.text_input(
                "Titre de l’incident",
                value=default_title,
            )

            left, right = st.columns(2)

            alert_level = (
                selected_alert.level
                if selected_alert.level in {
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL",
                }
                else "MEDIUM"
            )

            severity = left.selectbox(
                "Gravité",
                ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                index=[
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL",
                ].index(alert_level),
            )

            assigned_to = right.selectbox(
                "Attribué à",
                ANALYST_OPTIONS,
            )

            description = st.text_area(
                "Contexte et première analyse",
                value=(
                    f"Alerte #{selected_alert.id}\n"
                    f"Utilisateur : {selected_alert.user}\n"
                    f"Score : {selected_alert.score}/100\n"
                    f"Raisons : {selected_alert.reason}"
                ),
                height=150,
            )

            create_incident = st.form_submit_button(
                "Ouvrir l’incident",
                type="primary",
            )

        if create_incident:
            existing = (
                session.query(Incident)
                .filter(Incident.alert_id == selected_alert.id)
                .first()
            )

            if existing:
                st.warning(
                    f"Un incident existe déjà pour l’alerte #{selected_alert.id}."
                )
            else:
                incident = Incident(
                    alert_id=selected_alert.id,
                    title=title,
                    severity=severity,
                    status="NEW",
                    assigned_to=assigned_to,
                    description=description,
                    comments="",
                )

                selected_alert.status = "IN_PROGRESS"

                session.add(incident)
                session.commit()

                st.success("Incident créé avec succès.")
                st.rerun()

    st.divider()
    st.subheader("Suivi des incidents")

    if not incidents:
        st.info("Aucun incident créé pour le moment.")

    for incident in incidents:
        severity = (
            incident.severity
            if incident.severity in {
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            }
            else "MEDIUM"
        )

        status = (
            incident.status
            if incident.status in STATUS_OPTIONS
            else "NEW"
        )

        assignee = (
            incident.assigned_to
            if incident.assigned_to in ANALYST_OPTIONS
            else "Unassigned"
        )

        icon = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🔵",
        }[severity]

        with st.expander(
            f"{icon} Incident #{incident.id} · {status} · {incident.title}",
            expanded=status in {"NEW", "INVESTIGATING"},
        ):
            st.write(f"**Gravité :** {severity}")
            st.write(f"**Attribué à :** {assignee}")
            st.write(f"**Alerte source :** #{incident.alert_id}")

            st.write("**Description :**")
            st.write(incident.description or "Aucune description.")

            if incident.comments:
                st.write("**Journal analyste :**")
                st.code(incident.comments, language=None)

            st.divider()
            st.write("**Actions de réponse simulées**")
            st.caption(
                "Ces actions modifient la décision dans Sentinel IA "
                "et sont enregistrées dans l’audit log."
            )

            action_columns = st.columns(5)

            for column, (label, action) in zip(
                action_columns,
                RESPONSE_ACTIONS,
            ):
                with column:
                    if st.button(
                        label,
                        key=f"{action}_{incident.id}",
                    ):
                        actor = (
                            assignee
                            if assignee != "Unassigned"
                            else "SOC Analyst"
                        )

                        result = apply_response_action(
                            session,
                            incident,
                            action,
                            actor,
                        )

                        st.success(f"Action appliquée : {result}")
                        st.rerun()

            st.divider()

            with st.form(f"update_incident_{incident.id}"):
                new_status = st.selectbox(
                    "Statut",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(status),
                )

                new_assignee = st.selectbox(
                    "Attribué à",
                    ANALYST_OPTIONS,
                    index=ANALYST_OPTIONS.index(assignee),
                )

                new_comment = st.text_area(
                    "Ajouter une note analyste",
                    key=f"comment_{incident.id}",
                )

                save = st.form_submit_button(
                    "Enregistrer les modifications"
                )

            if save:
                incident.status = new_status
                incident.assigned_to = new_assignee

                if new_comment.strip():
                    timestamp = datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d %H:%M UTC"
                    )
                    incident.comments = (
                        f"{incident.comments or ''}"
                        f"\n[{timestamp}] {new_comment.strip()}"
                    ).strip()

                if new_status in {"RESOLVED", "CLOSED"}:
                    incident.resolved_at = datetime.now(timezone.utc)

                source_alert = (
                    session.query(Alert)
                    .filter(Alert.id == incident.alert_id)
                    .first()
                )

                if source_alert:
                    source_alert.status = (
                        "RESOLVED"
                        if new_status in {"RESOLVED", "CLOSED"}
                        else "IN_PROGRESS"
                    )

                session.commit()
                st.success("Incident mis à jour.")
                st.rerun()

finally:
    session.close()