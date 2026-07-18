import streamlit as st

from database.database import SessionLocal
from models.alert import Alert


st.set_page_config(
    page_title="Alertes Sentinel AI",
    page_icon="🚨"
)


st.title("🚨 Centre des alertes")



session = SessionLocal()


alerts = session.query(Alert).all()



if not alerts:

    st.success(
        "Aucune alerte détectée"
    )


else:


    for alert in alerts:


        text = f"""
Utilisateur : {alert.user}

Niveau : {alert.level}

Score : {alert.score}/100

Raison :

{alert.reason}
"""


        if alert.level == "CRITICAL":

            st.error(text)


        elif alert.level == "HIGH":

            st.warning(text)


        else:

            st.info(text)



session.close()