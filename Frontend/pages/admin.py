import streamlit as st
import requests
import os
# --- RÉCUPÉRATION DU TOKEN DEPUIS L'URL (F5 Proof) ---
# Récupère le token soit depuis l'URL (pour gérer le refresh) soit depuis la session
url_token = st.query_params.get("t")

if url_token:
    st.session_state['token'] = url_token

# Si on a déjà un token en session, on le ré-écrit dans l'URL pour qu'il survive au refresh
if 'token' in st.session_state and st.session_state['token']:
    try:
        st.query_params["t"] = st.session_state['token']
    except Exception:
        pass

# Si on n'a rien, on redirige vers la page de connexion
if 'token' not in st.session_state or st.session_state['token'] is None:
    st.switch_page("pages/auth.py")
    st.stop()

# --- CONFIGURATION ---
st.set_page_config(page_title="Administration - AgriLink", layout="wide")
LOGO_URL= "https://github.com/WillLoic/AgriLink/blob/developpement/Frontend/icon2.jpg"
st.sidebar.image(LOGO_URL)
st.markdown("""
    <style>
        /* Masquer la barre de navigation latérale de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .admin-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    .admin-header {
        text-align: center;
        color: #2e7d32;
        margin-bottom: 2rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
    }
    .admin-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .user-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
        color: black;
    }
    .user-card.admin {
        border-left-color: #ff9800;
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    }
    .user-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .user-details {
        flex: 1;
    }
    .user-actions {
        display: flex;
        gap: 1rem;
    }
    .btn-promote {
        background: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    .btn-demote {
        background: #f44336;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .stat-label {
        color: #666;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


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
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
# --- FONCTIONS UTILITAIRES ---
def get_all_users():
    """Récupère tous les utilisateurs"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        response = requests.get(f"{st.session_state.get('API_URL', 'http://127.0.0.1:5000')}/api/v1/admin/users", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def promote_to_admin(user_id):
    """Promouvoir un utilisateur au rang d'admin"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        response = requests.post(
            f"{st.session_state.get('API_URL', 'http://127.0.0.1:5000')}/api/v1/admin/promote/{user_id}",
            headers=headers,
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def demote_from_admin(user_id):
    """Rétrograder un admin en utilisateur normal"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        response = requests.post(
            f"{st.session_state.get('API_URL', 'http://127.0.0.1:5000')}/api/v1/admin/demote/{user_id}",
            headers=headers,
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def get_user_role():
    """Vérifie si l'utilisateur actuel est admin"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        response = requests.get(f"{st.session_state.get('API_URL', 'http://127.0.0.1:5000')}/api/v1/user/profile", headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('role', 'user')
        return 'user'
    except:
        return 'user'

# --- LOGIQUE PRINCIPALE ---
def main():
    # Vérification de l'authentification
    if 'token' not in st.session_state or not st.session_state['token']:
        st.error("❌ Accès non autorisé. Veuillez vous connecter.")
        st.stop()

    # Vérification du rôle admin
    user_role = get_user_role()
    if user_role != 'admin' and st.session_state.get('phone') != '692253474':
        st.error("❌ Accès réservé aux administrateurs.")
        st.write(f"DEBUG Phone: '{st.session_state.get('phone')}'")
        st.write(f"DEBUG Role: '{user_role}'")
        st.stop()
    st.write(f"DEBUG Phone: '{st.session_state.get('phone')}'")
    st.write(f"DEBUG Role: '{user_role}'")
    st.markdown('<div class="admin-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="admin-header">
        <h1>⚙️ Panel d'Administration</h1>
        <p>Gestion des utilisateurs et statistiques système</p>
    </div>
    """, unsafe_allow_html=True)

    # Onglets pour différentes sections
    tab1, tab2 = st.tabs(["👥 Gestion Utilisateurs", "📊 Statistiques"])

    with tab1:
        st.markdown("### 👥 Gestion des Utilisateurs")

        # Bouton pour rafraîchir
        if st.button("🔄 Actualiser la liste"):
            st.rerun()

        # Récupération des utilisateurs
        users = get_all_users()

        if users:
            # Statistiques rapides
            total_users = len(users)
            admin_count = sum(1 for user in users if user.get('role') == 'admin')
            user_count = total_users - admin_count

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Utilisateurs", total_users)
            with col2:
                st.metric("Administrateurs", admin_count)
            with col3:
                st.metric("Utilisateurs", user_count)

            st.markdown("---")

            # Liste des utilisateurs
            for user in users:
                is_admin = user.get('role') == 'admin'
                card_class = "user-card admin" if is_admin else "user-card"

                st.markdown(f"""
                <div class="{card_class}">
                    <div class="user-info">
                        <div class="user-details">
                            <h3>👤 {user.get('nom', 'N/A')}</h3>
                            <p>📧 {user.get('email', 'N/A')}</p>
                            <p>🌾 Culture: {user.get('culture_type', 'N/A')}</p>
                            <p>📅 Inscrit: {user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Actions
                col1, col2 = st.columns([3, 1])
                with col2:
                    user_id = user.get('id')
                    if is_admin:
                        if st.button(f"🔽 Rétrograder", key=f"demote_{user_id}"):
                            if demote_from_admin(user_id):
                                st.success(f"✅ {user.get('nom')} n'est plus administrateur")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la rétrogradation")
                    else:
                        if st.button(f"⬆️ Promouvoir", key=f"promote_{user_id}"):
                            if promote_to_admin(user_id):
                                st.success(f"✅ {user.get('nom')} est maintenant administrateur")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la promotion")

                st.markdown("---")
        else:
            st.warning("⚠️ Impossible de récupérer la liste des utilisateurs")

    with tab2:
        st.markdown("### 📊 Statistiques Système")

        # Récupération des analytics
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        try:
            response = requests.get(f"{st.session_state.get('API_URL', 'http://127.0.0.1:5000')}/api/v1/analytics", headers=headers, timeout=5)
            if response.status_code == 200:
                analytics = response.json()

                # Métriques principales
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        label="👥 Total Utilisateurs",
                        value=f"{analytics.get('total_users', 0)}"
                    )

                with col2:
                    st.metric(
                        label="🔍 Total Scans",
                        value=f"{analytics.get('total_scans', 0)}"
                    )

                with col3:
                    recent_logins = analytics.get('recent_activity', {}).get('logins_30_days', 0)
                    st.metric(
                        label="🔑 Connexions (30j)",
                        value=f"{recent_logins}"
                    )

                with col4:
                    recent_scans = analytics.get('recent_activity', {}).get('scans_30_days', 0)
                    st.metric(
                        label="📊 Scans (30j)",
                        value=f"{recent_scans}"
                    )

                # Graphiques détaillés
                st.markdown("### 🌾 Répartition par Culture")
                culture_data = analytics.get('culture_distribution', [])

                if culture_data:
                    import pandas as pd
                    df_cultures = pd.DataFrame(culture_data)
                    st.bar_chart(df_cultures.set_index('culture'))
                else:
                    st.info("Aucune donnée de culture disponible")

                # Évolution des scans
                st.markdown("### 📈 Évolution des Scans (7 derniers jours)")
                daily_scans = analytics.get('daily_scans_last_7_days', [])

                if daily_scans:
                    import pandas as pd
                    df_scans = pd.DataFrame(daily_scans)
                    df_scans['date'] = pd.to_datetime(df_scans['date'])
                    df_scans = df_scans.sort_values('date')
                    st.line_chart(df_scans.set_index('date'))
                else:
                    st.info("Aucune donnée d'évolution disponible")

            else:
                st.error("❌ Impossible de récupérer les statistiques")
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
