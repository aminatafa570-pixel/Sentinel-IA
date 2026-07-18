import pandas as pd
import pydeck as pdk
import streamlit as st

from database.database import SessionLocal
from models.event import Event


st.set_page_config(
    page_title="Carte mondiale Sentinel IA",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Carte mondiale des connexions")
st.caption(
    "Les nouvelles simulations apparaissent automatiquement "
    "sur la carte toutes les 10 secondes."
)

COUNTRY_COORDINATES = {
    "Senegal": {"latitude": 14.7167, "longitude": -17.4677},
    "France": {"latitude": 48.8566, "longitude": 2.3522},
    "USA": {"latitude": 38.9072, "longitude": -77.0369},
    "Russia": {"latitude": 55.7558, "longitude": 37.6173},
    "China": {"latitude": 39.9042, "longitude": 116.4074},
    "Germany": {"latitude": 52.5200, "longitude": 13.4050},
    "United Kingdom": {"latitude": 51.5072, "longitude": -0.1276},
}

DECISION_COLORS = {
    "ALLOWED": [34, 197, 94, 180],
    "MFA_REQUIRED": [234, 179, 8, 190],
    "TEMP_BLOCK": [249, 115, 22, 200],
    "BLOCKED": [239, 68, 68, 220],
}


@st.fragment(run_every="10s")
def render_live_map():
    session = SessionLocal()

    try:
        events = (
            session.query(Event)
            .order_by(Event.id.desc())
            .limit(200)
            .all()
        )

        map_rows = []

        for event in events:
            location = event.location or "UNKNOWN"
            coordinates = COUNTRY_COORDINATES.get(location)

            if not coordinates:
                continue

            decision = event.security_action or "UNKNOWN"

            timestamp = (
                event.timestamp.strftime("%d/%m/%Y %H:%M UTC")
                if event.timestamp
                else "Date indisponible"
            )

            map_rows.append({
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
                "color": DECISION_COLORS.get(
                    decision,
                    [148, 163, 184, 160],
                ),
                "radius": 80000 + (event.risk_score or 0) * 2500,
                "Utilisateur": event.user or "UNKNOWN",
                "Pays": location,
                "IP": event.ip_address or "UNKNOWN",
                "Appareil": event.device or "UNKNOWN",
                "Score": f"{event.risk_score or 0}/100",
                "Décision": decision,
                "Date": timestamp,
                "Raisons": event.risk_reasons or "Non disponible",
            })

        dataframe = pd.DataFrame(map_rows)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Connexions affichées", len(dataframe))
        col2.metric(
            "Blocages immédiats",
            sum(
                row["Décision"] == "BLOCKED"
                for row in map_rows
            ),
        )
        col3.metric(
            "Blocages temporaires",
            sum(
                row["Décision"] == "TEMP_BLOCK"
                for row in map_rows
            ),
        )
        col4.metric(
            "Vérifications MFA",
            sum(
                row["Décision"] == "MFA_REQUIRED"
                for row in map_rows
            ),
        )

        st.divider()

        if dataframe.empty:
            st.info(
                "Aucune connexion géolocalisable pour le moment. "
                "Lance une simulation."
            )
            return

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=dataframe,
            get_position="[longitude, latitude]",
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
            opacity=0.8,
            stroked=True,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1,
        )

        # --- CORRECTION ICI ---
        # Avant : map_style="mapbox://styles/mapbox/dark-v11" (nécessitait un token Mapbox absent -> fond de carte invisible)
        # Après : map_provider="carto" + map_style="dark" (gratuit, sans inscription, sans token)
        deck = pdk.Deck(
            map_provider="carto",
            map_style="dark",
            initial_view_state=pdk.ViewState(
                latitude=25,
                longitude=10,
                zoom=1.15,
                pitch=0,
            ),
            layers=[layer],
            tooltip={
                "html": (
                    "<b>{Utilisateur}</b><br/>"
                    "Pays : {Pays}<br/>"
                    "IP : {IP}<br/>"
                    "Appareil : {Appareil}<br/>"
                    "Score : {Score}<br/>"
                    "Décision : {Décision}<br/>"
                    "Date : {Date}<br/>"
                    "Raisons : {Raisons}"
                ),
                "style": {
                    "backgroundColor": "#111827",
                    "color": "white",
                },
            },
        )

        st.pydeck_chart(deck, use_container_width=True)

        st.caption(
            "Légende : vert = autorisé, jaune = MFA, "
            "orange = blocage temporaire, rouge = blocage immédiat."
        )

        st.subheader("Dernières connexions géolocalisées")

        st.dataframe(
            dataframe[
                [
                    "Date",
                    "Utilisateur",
                    "Pays",
                    "IP",
                    "Appareil",
                    "Score",
                    "Décision",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    finally:
        session.close()


render_live_map()