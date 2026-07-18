import streamlit as st

from database.database import SessionLocal
from models.event import Event
from security.recommendation_engine import generate_recommendations


st.set_page_config(
    page_title="Recommandations Sentinel IA",
    page_icon="💡",
    layout="wide",
)

st.title("💡 Recommandations Sentinel IA")
st.caption(
    "Actions proposées à partir du score, des raisons de risque "
    "et du contexte de connexion."
)

session = SessionLocal()

try:
    events = (
        session.query(Event)
        .order_by(Event.id.desc())
        .limit(200)
        .all()
    )

    if not events:
        st.info("Aucun événement à analyser. Lance une simulation.")
    else:
        event_options = {
            (
                f"#{event.id} · {event.user} · "
                f"{event.action} · score {event.risk_score or 0}/100"
            ): event
            for event in events
        }

        selected_label = st.selectbox(
            "Événement à analyser",
            list(event_options.keys()),
        )
        event = event_options[selected_label]

        recommendation = generate_recommendations(event)

        col1, col2, col3 = st.columns(3)
        col1.metric("Score de risque", f"{event.risk_score or 0}/100")
        col2.metric("Décision", event.security_action or "UNKNOWN")
        col3.metric("Priorité recommandée", recommendation["priority"])

        st.divider()
        st.subheader("Analyse Sentinel IA")
        st.info(recommendation["summary"])

        st.subheader("Pourquoi cet événement est-il signalé ?")
        st.write(event.risk_reasons or "Aucune raison détaillée disponible.")

        st.subheader("Actions recommandées")

        for index, action in enumerate(recommendation["actions"], start=1):
            st.write(f"{index}. {action}")

        st.caption(
            "Ces recommandations assistent l’analyste ; "
            "la décision finale reste traçable dans le centre d’incidents."
        )

finally:
    session.close()