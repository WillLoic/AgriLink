import streamlit as st
import requests
from datetime import datetime

st.markdown("""
    <style>
        /* Masquer la barre de navigation latérale de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)


# --- CONFIGURATION ---
st.set_page_config(page_title="Réinitialiser mot de passe - AgriLink", layout="centered")

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .reset-password-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .reset-password-header {
        text-align: center;
        color: #2e7d32;
        margin-bottom: 2rem;
    }
    .reset-password-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .reset-password-header p {
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
    .password-strength {
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .password-strength.weak {
        color: #f44336;
    }
    .password-strength.medium {
        color: #ff9800;
    }
    .password-strength.strong {
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def check_password_strength(password):
    """Vérifie la force du mot de passe"""
    if len(password) < 6:
        return "weak", "❌ Trop court (minimum 6 caractères)"
        """elif len(password) < 8:
            return "medium", "⚠️ Faible (ajoutez des chiffres ou symboles)"
        elif not any(char.isdigit() for char in password):
            return "medium", "⚠️ Moyen (ajoutez au moins un chiffre)"
        elif not any(char.isupper() for char in password):
            return "medium", "⚠️ Moyen (ajoutez au moins une majuscule)"
            """
    else:
        return "strong", "✅ OK"

# --- LOGIQUE PRINCIPALE ---
def main():
    # Récupérer le token depuis les paramètres d'URL
    query_params = st.query_params
    token = query_params.get("token")
    if isinstance(token, list):
        token = token[0] if token else None

    if not token:
        st.error("❌ Lien de réinitialisation invalide ou manquant.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Retour à la connexion", use_container_width=False):
            st.switch_page("pages/auth.py")
        return

    st.markdown('<div class="reset-password-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="reset-password-header">
        <h1>🔑 Nouveau mot de passe</h1>
        <p>Choisissez un nouveau mot de passe sécurisé</p>
    </div>
    """, unsafe_allow_html=True)

    # Formulaire de réinitialisation
    with st.form("reset_password_form"):
        new_password = st.text_input(
            "🔒 Nouveau mot de passe",
            type="password",
            help="Minimum 6 caractères avec chiffres et majuscules"
        )

        confirm_password = st.text_input(
            "🔒 Confirmer le mot de passe",
            type="password",
            help="Retapez le même mot de passe"
        )

        # Vérification de la force du mot de passe
        if new_password:
            strength_class, strength_text = check_password_strength(new_password)
            st.markdown(f"""
            <div class="password-strength {strength_class}">
                {strength_text}
            </div>
            """, unsafe_allow_html=True)

        submitted = st.form_submit_button("💾 Réinitialiser le mot de passe")

        if submitted:
            if not new_password or not confirm_password:
                st.error("Veuillez remplir tous les champs.")
            elif new_password != confirm_password:
                st.error("Les mots de passe ne correspondent pas.")
            elif len(new_password) < 6:
                st.error("Le mot de passe doit contenir au moins 6 caractères.")
            else:
                with st.spinner("Réinitialisation du mot de passe..."):
                    try:
                        API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
                        response = requests.post(
                            f"{API_URL}/api/v1/reset-password",
                            data={
                                "token": token,
                                "new_password": new_password
                            },
                            timeout=10
                        )

                        if response.status_code == 200:
                            st.success("✅ Mot de passe réinitialisé avec succès !")
                            st.markdown("""
                            <div class="success-message">
                                <strong>🎉 Réinitialisation réussie !</strong><br>
                                Votre mot de passe a été changé. Vous pouvez maintenant vous connecter.
                            </div>
                            """, unsafe_allow_html=True)

                            # Redirection automatique après 3 secondes
                            import time
                            time.sleep(2)
                            st.switch_page("pages/auth.py")

                        else:
                            error_data = response.json()
                            st.error(f"❌ {error_data.get('error', 'Erreur lors de la réinitialisation')}")

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
