import streamlit as st


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display:none;}
            [data-testid="stToolbar"] {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# --- REDIRECTION VERS LANDING PAGE ---
# Ce fichier sert de point d'entrée principal
# Il redirige automatiquement vers la landing page
st.switch_page("pages/landing.py")
