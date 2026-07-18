import streamlit as st


st.set_page_config(
    page_title="Analyse IA",
    page_icon="🤖"
)


st.title("🤖 Intelligence Artificielle")



st.write(
"""
Sentinel AI utilise un modèle
Isolation Forest pour détecter
les comportements anormaux.
"""
)



col1, col2, col3 = st.columns(3)



with col1:

    st.metric(
        "Algorithme",
        "Isolation Forest"
    )


with col2:

    st.metric(
        "Features",
        "3"
    )


with col3:

    st.metric(
        "Statut",
        "ACTIF 🟢"
    )