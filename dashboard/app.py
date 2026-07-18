import random

import pandas as pd
import streamlit as st

from database.database import Base, SessionLocal, engine
from engine.event_processor import process_event
from models.alert import Alert
from models.event import Event
from security.risk_engine import RiskEngine


Base.metadata.create_all(engine)

st.set_page_config(
    page_title="Sentinel IA | Security Operations",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; }
        [data-testid="stMetric"] {
            background: #111827;
            border: 1px solid #263244;
            border-radius: 12px;
            padding: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛡️ Sentinel IA")
st.caption("Security Operations Center · Détection, analyse et réponse aux menaces")

risk_engine = RiskEngine()

SCENARIOS = {
    "Connexion normale — autorisée": {
        "user": "Marie",
        "action": "LOGIN",
        "location": "France",
        "hour": 10,
        "status": "SUCCESS",
        "ip_address": "82.64.10.25",
        "device": "Chrome · Windows 11",
        "network_type": "Corporate network",
    },
    "Pays inhabituel — vérification MFA": {
        "user": "John",
        "action": "LOGIN",
        "location": "USA",
        "hour": 14,
        "status": "SUCCESS",
        "ip_address": "104.28.12.51",
        "device": "Safari · macOS",
        "network_type": "Residential network",
    },
    "Échec de connexion — vérification MFA": {
        "user": "Ahmed",
        "action": "LOGIN",
        "location": "France",
        "hour": 11,
        "status": "FAILED",
        "ip_address": "90.12.67.40",
        "device": "Chrome · Windows 11",
        "network_type": "Corporate network",
    },
    "Connexion nocturne étrangère — blocage temporaire": {
        "user": "Marie",
        "action": "LOGIN",
        "location": "USA",
        "hour": 2,
        "status": "SUCCESS",
        "ip_address": "104.28.12.51",
        "device": "Unknown device",
        "network_type": "VPN",
    },
    "Brute force étranger — blocage temporaire": {
        "user": "Ahmed",
        "action": "LOGIN",
        "location": "Russia",
        "hour": 14,
        "status": "FAILED",
        "ip_address": "185.220.101.14",
        "device": "Unknown device",
        "network_type": "Proxy",
    },
    "Tentative Tor critique — blocage immédiat": {
        "user": "Marie",
        "action": "PASSWORD_RESET",
        "location": "China",
        "hour": 1,
        "status": "FAILED",
        "ip_address": "45.155.205.13",
        "device": "Unknown device",
        "network_type": "Tor",
    },
}

with st.container(border=True):
    left, right = st.columns([2, 1])

    with left:
        st.subheader("⚔️ Simulateur d’attaque")
        selected_scenario = st.selectbox(
            "Scénario à exécuter",
            list(SCENARIOS.keys()),
        )

    with right:
        st.write("")
        st.write("")
        run_simulation = st.button(
            "Lancer la simulation",
            type="primary",
            use_container_width=True,
        )

if run_simulation:
    event_data = SCENARIOS[selected_scenario].copy()

    # Variation légère afin que les simulations ne soient pas identiques.
    event_data["ip_address"] = (
        event_data["ip_address"].rsplit(".", 1)[0]
        + f".{random.randint(10, 240)}"
    )

    session = SessionLocal()
    try:
        event = Event(**event_data)
        analysis, _ = process_event(session, event, risk_engine)

        decision = analysis["decision"]
        message = (
            f"Score : {analysis['score']}/100 · "
            f"Décision : {decision}"
        )

        if decision == "ALLOWED":
            st.success(f"🟢 Simulation terminée — {message}")
        elif decision == "MFA_REQUIRED":
            st.warning(f"🟡 Vérification renforcée requise — {message}")
        elif decision == "TEMP_BLOCK":
            st.warning(f"🟠 Blocage temporaire appliqué — {message}")
        else:
            st.error(f"🔴 Menace critique bloquée — {message}")

        st.info(
            "**Raisons de Sentinel IA :** "
            + " · ".join(analysis["reasons"])
        )
    finally:
        session.close()

session = SessionLocal()
try:
    events = (
        session.query(Event)
        .order_by(Event.id.desc())
        .limit(300)
        .all()
    )
    alerts = (
        session.query(Alert)
        .order_by(Alert.id.desc())
        .limit(100)
        .all()
    )
finally:
    session.close()

event_rows = [
    {
        "ID": event.id,
        "Date / heure": event.timestamp,
        "Utilisateur": event.user,
        "Action": event.action,
        "Pays": event.location,
        "IP": event.ip_address or "UNKNOWN",
        "Appareil": event.device or "UNKNOWN",
        "Réseau": event.network_type or "UNKNOWN",
        "Statut": event.status,
        "Score": event.risk_score or 0,
        "Niveau": event.risk_level or "UNKNOWN",
        "Décision": event.security_action or "UNKNOWN",
        "Raisons": event.risk_reasons or "Analyse historique indisponible",
    }
    for event in events
]

df_events = pd.DataFrame(event_rows)

total_events = len(df_events)
open_alerts = sum(
    1 for alert in alerts if (alert.status or "OPEN") == "OPEN"
)
blocked = (
    int((df_events["Décision"] == "BLOCKED").sum())
    if not df_events.empty
    else 0
)
average_risk = (
    round(float(df_events["Score"].mean()), 1)
    if not df_events.empty
    else 0
)

st.divider()
st.subheader("Vue opérationnelle")

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Événements analysés", total_events)
metric_2.metric("Alertes ouvertes", open_alerts)
metric_3.metric("Blocages immédiats", blocked)
metric_4.metric("Risque moyen", f"{average_risk}/100")

if not df_events.empty:
    st.divider()
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.subheader("Décisions Sentinel IA")
        st.bar_chart(
            df_events["Décision"].value_counts(),
            color="#38bdf8",
        )

    with chart_right:
        st.subheader("Alertes par niveau de gravité")
        st.bar_chart(
            df_events["Niveau"].value_counts(),
            color="#f97316",
        )

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.subheader("Connexions par pays")
        st.bar_chart(
            df_events["Pays"].value_counts().head(10),
            color="#a78bfa",
        )

    with chart_right:
        st.subheader("Utilisateurs les plus signalés")
        suspicious = df_events[df_events["Score"] >= 30]
        if suspicious.empty:
            st.info("Aucun utilisateur signalé pour le moment.")
        else:
            st.bar_chart(
                suspicious["Utilisateur"].value_counts(),
                color="#ef4444",
            )

    st.divider()
    st.subheader("Historique des événements")

    filter_left, filter_right, filter_third = st.columns(3)
    user_filter = filter_left.multiselect(
        "Utilisateurs",
        sorted(df_events["Utilisateur"].dropna().unique()),
    )
    decision_filter = filter_right.multiselect(
        "Décisions",
        sorted(df_events["Décision"].dropna().unique()),
    )
    minimum_score = filter_third.slider(
        "Score de risque minimum",
        min_value=0,
        max_value=100,
        value=0,
    )

    filtered_events = df_events.copy()
    if user_filter:
        filtered_events = filtered_events[
            filtered_events["Utilisateur"].isin(user_filter)
        ]
    if decision_filter:
        filtered_events = filtered_events[
            filtered_events["Décision"].isin(decision_filter)
        ]

    filtered_events = filtered_events[
        filtered_events["Score"] >= minimum_score
    ]

    st.dataframe(
        filtered_events,
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("🚨 Centre des alertes")

if alerts:
    alert_rows = [
        {
            "Alerte": alert.id,
            "Événement": alert.event_id or "Historique",
            "Utilisateur": alert.user,
            "Niveau": alert.level,
            "Score": alert.score,
            "Statut": alert.status or "OPEN",
            "Raisons": alert.reason,
        }
        for alert in alerts
    ]
    st.dataframe(
        pd.DataFrame(alert_rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("Aucune alerte à traiter.")