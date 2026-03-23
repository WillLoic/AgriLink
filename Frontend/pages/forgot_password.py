import streamlit as st
import requests
from datetime import datetime
import os

# --- CONFIGURATION ---

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

st.set_page_config(page_title="Mot de passe oublié - AgriLink", layout="centered")

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .forgot-password-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .forgot-password-header {
        text-align: center;
        color: #2e7d32;
        margin-bottom: 2rem;
    }
    .forgot-password-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .forgot-password-header p {
        color: #666;
        font-size: 1.1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #45a049, #4CAF50);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }
    .back-link {
        text-align: center;
        margin-top: 1rem;
    }
    .back-link a {
        color: #4CAF50;
        text-decoration: none;
        font-weight: bold;
    }
    .back-link a:hover {
        text-decoration: underline;
    }
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f44336;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE PRINCIPALE ---
def main():
    st.markdown('<div class="forgot-password-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="forgot-password-header">
        <h1>🔐 Mot de passe oublié</h1>
        <p>Entrez votre email pour recevoir un lien de réinitialisation</p>
    </div>
    """, unsafe_allow_html=True)

    # Formulaire de récupération
    with st.form("forgot_password_form"):
        email = st.text_input(
            "📧 Email",
            placeholder="votre.email@exemple.com",
            help="Entrez l'email associé à votre compte AgriLink"
        )

        submitted = st.form_submit_button("📤 Envoyer le lien de réinitialisation")

        if submitted:
            if not email:
                st.error("Veuillez saisir votre email.")
            elif "@" not in email:
                st.error("Veuillez saisir un email valide.")
            else:
                with st.spinner("Envoi du lien de réinitialisation..."):
                    try:
                        API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
                        response = requests.post(
                            f"{API_URL}/api/v1/forgot-password",
                            json={"email": email},
                            timeout=50
                        )

                        if response.status_code == 200:
                            st.success("✅ Lien de réinitialisation envoyé !")
                            st.markdown("""
                            <div class="success-message">
                                <strong>📧 Vérifiez votre boîte mail</strong><br>
                                Un email contenant un lien de réinitialisation vous a été envoyé.
                                Le lien expirera dans 1 heure.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # On essaie de lire l'erreur proprement
                                    try:
                                        error_msg = response.json().get('error', 'Erreur inconnue')
                                    except:
                                        error_msg = f"Le serveur a répondu avec le code {response.status_code}"
                                    st.error(f"❌ {error_msg}")

                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Erreur de connexion au serveur : {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Erreur inattendue : {str(e)}")

    # Bouton de retour
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Retour à la connexion", use_container_width=False):
        st.switch_page("pages/auth.py")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
