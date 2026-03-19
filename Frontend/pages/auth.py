import streamlit as st
import requests
import time
from streamlit_js_eval import get_geolocation
import json



# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AgriLink - Analyse Agricole IA",
    page_icon="🌱",
    layout="centered"
)
st.markdown("""
    <style>
        /* Masquer la barre de navigation latérale de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- STYLE PERSONNALISÉ (CSS) ---
st.markdown("""
    <style>
        <style>
            
    .stButton>button {
        background-color: #2ECC71;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-color: #2ECC71;
    }
    h1 { color: #27AE60; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "http://127.0.0.1:5000"

# --- GESTION DE LA SESSION ---
if 'token' not in st.session_state:
    st.session_state['token'] = None

# --- REDIRECTION AUTOMATIQUE ---
# Si l'utilisateur est déjà connecté, on l'envoie direct au dashboard
if st.session_state['token'] is not None:
    st.switch_page("pages/dashboard.py")

def login_user(phone, password):
    try:
        # Rigueur : Vérifie que l'URL correspond bien à ton @app.route du Backend
        response = requests.post(f"{API_URL}/api/v1/login", data={'phone': phone, 'password': password})
        if response.status_code == 200:
            data = response.json()
            st.session_state['token'] = data.get('token')
            return True
        return False
    except Exception as e:
        st.error(f"Erreur de connexion au serveur : {e}")
        return False

# --- UI : LOGIN / REGISTER ---
st.title("🌱 AgriLink")
st.write("Bienvenue sur votre plateforme d'analyse agricole par IA.")

tab1, tab2 = st.tabs(["Connexion", "Inscription"])

with tab1:
    with st.form("login_form"):
        phone = st.text_input("Numéro de téléphone")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

        if submitted:
            if login_user(phone, password):
                # On stocke le token dans l'URL pour qu'il survive au rafraîchissement
                token = st.session_state['token']
                try:
                    st.query_params["t"] = token
                except Exception:
                    pass

                st.success("Connexion réussie ! Redirection...")
                time.sleep(0.5)
                st.switch_page("pages/dashboard.py")
            else:
                st.error("Identifiants incorrects.")

    # Bouton vers mot de passe oublié
    st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
    if st.button("🔐 Mot de passe oublié ?", use_container_width=False):
        st.switch_page("pages/forgot_password.py")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    if 'points_gps' not in st.session_state:
        st.session_state['points_gps'] = []

    st.subheader("Créer un compte agriculteur")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet")
            email = st.text_input("Email")
            phone_reg = st.text_input("Numéro de téléphone")
        with col2:
            password_reg = st.text_input("Mot de passe", type="password")
            culture = st.selectbox("Type de culture", ["Maïs", "Riz", "Cacao", "Café", "Manioc"])

        st.write("---")
        st.write("📍 **Délimitation de la parcelle**")
        
        if st.session_state['points_gps']:
            st.write(f"✅ {len(st.session_state['points_gps'])} points enregistrés")
        
        submitted_reg = st.form_submit_button("Finaliser l'inscription")

    # Capture GPS Hors Formulaire
    loc = get_geolocation()
    col_gps1, col_gps2 = st.columns(2)
    with col_gps1:
        if st.button("📌 Ajouter l'angle actuel"):
            if loc:
                lat = loc['coords']['latitude']
                lng = loc['coords']['longitude']
                st.session_state['points_gps'].append([lat, lng])
                st.rerun()
            else:
                st.warning("Activez le GPS.")
    with col_gps2:
        if st.button("🗑️ Reset points"):
            st.session_state['points_gps'] = []
            st.rerun()

    if submitted_reg:
        if len(st.session_state['points_gps']) < 3:
            st.error("Besoin de 3 points minimum.")
        else:
            data_reg = {
                "nom": nom, "email": email, "phone": phone_reg,
                "password": password_reg, "culture_type": culture,
                "coords": json.dumps(st.session_state['points_gps'])
            }
            res = requests.post(f"{API_URL}/api/v1/register", data=data_reg)
            
            if res.status_code == 200:
                st.success("Compte créé !")
                if login_user(phone_reg, password_reg):
                    # On stocke le token dans l'URL pour qu'il ne disparaisse pas après un refresh
                    token = st.session_state['token']
                    try:
                        st.query_params["t"] = token
                    except Exception:
                        pass

                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Erreur lors de l'inscription.")


