import streamlit as st
import requests

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
API_URL = "http://127.0.0.1:5000"

# --- CONFIGURATION ---
st.set_page_config(page_title="Dashboard - AgriLink", layout="wide")
st.markdown("""
    <style>
        /* Masquer la barre de navigation latérale de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

def get_dashboard_stats():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        # Rigueur : Vérifie que le endpoint est exactement /api/v1/dashboard/stats
        res = requests.get(f"{API_URL}/api/v1/dashboard/stats", headers=headers)
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None
def get_pdf_report():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        res = requests.get(f"{API_URL}/api/v1/dashboard/certificat", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.content
        return None
    except:
        return None

def get_user_role():
    """Récupère le rôle de l'utilisateur connecté"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        response = requests.get(f"{API_URL}/api/v1/user/profile", headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('role', 'user')
        return 'user'
    except:
        return 'user'

def get_analytics_data():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        res = requests.get(f"{API_URL}/api/v1/analytics", headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None


# --- SÉCURITÉ : VÉRIFICATION DU TOKEN ---
if 'token' not in st.session_state or st.session_state['token'] is None:
    st.warning("⚠️ Session expirée. Veuillez vous reconnecter.")
    st.switch_page("pages/auth.py")
    st.stop()

# --- RÉCUPÉRATION DES DONNÉES ---
stats = get_dashboard_stats()

# --- INTERFACE ---
if stats:
    st.title(f"📊 Dashboard : {stats.get('agriculteur', 'Mon Exploitation')}")
    
    # --- SCORE CARD ---
    score = stats.get('score', 0)
    color = "#2ECC71" if score >= 75 else "#F1C40F" if score >= 50 else "#E74C3C"
    
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 15px; border-left: 10px solid {color}; box-shadow: 0px 4px 12px rgba(0,0,0,0.08);">
            <h3 style="margin:0; color: #7F8C8D; font-size: 16px; text-transform: uppercase;">Score de Crédibilité</h3>
            <h1 style="margin:0; color: {color}; font-size: 60px; font-weight: bold;">{score} <span style="font-size: 20px; color: #BDC3C7;">/ 100</span></h1>
            <p style="margin-top:10px; color: #2C3E50; font-weight: 500;">📌 Statut : {stats.get('statut_confiance', 'Analyse en cours')}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("##")

    # --- METRICS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Scans Effectués", value=f"{stats.get('total_scans', 0)}")
    
    with col3:
        st.metric(label="Culture", value=stats.get('culture', 'N/A'))

    # Bouton d'accès au panel admin (pour les admins)
    user_role = get_user_role()
    if user_role == 'admin':
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚙️ Panel d'Administration", use_container_width=True, type="secondary"):
                st.switch_page("pages/admin.py")

    st.write("---")

    # --- ANALYTICS (ADMIN UNIQUEMENT) ---
    # Vérifier si l'utilisateur est admin
    if user_role == 'admin':
        st.markdown("## 📈 Statistiques Globales (Admin)")

        analytics_data = get_analytics_data()

        if analytics_data and 'error' not in analytics_data:
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="👥 Total Utilisateurs",
                    value=f"{analytics_data.get('total_users', 0)}"
                )

            with col2:
                st.metric(
                    label="🔍 Total Scans",
                    value=f"{analytics_data.get('total_scans', 0)}"
                )

            with col3:
                recent_logins = analytics_data.get('recent_activity', {}).get('logins_30_days', 0)
                st.metric(
                    label="🔑 Connexions (30j)",
                    value=f"{recent_logins}"
                )

            with col4:
                recent_scans = analytics_data.get('recent_activity', {}).get('scans_30_days', 0)
                st.metric(
                    label="📊 Scans (30j)",
                    value=f"{recent_scans}"
                )

            # Graphique de répartition des cultures
            st.markdown("### 🌾 Répartition par Culture")
            culture_data = analytics_data.get('culture_distribution', [])

            if culture_data:
                import pandas as pd

                df_cultures = pd.DataFrame(culture_data)
                st.bar_chart(df_cultures.set_index('culture'))
            else:
                st.info("Aucune donnée de culture disponible")

            # Évolution des scans sur 7 jours
            st.markdown("### 📈 Évolution des Scans (7 derniers jours)")
            daily_scans = analytics_data.get('daily_scans_last_7_days', [])

            if daily_scans:
                import pandas as pd

                df_scans = pd.DataFrame(daily_scans)
                df_scans['date'] = pd.to_datetime(df_scans['date'])
                df_scans = df_scans.sort_values('date')
                st.line_chart(df_scans.set_index('date'))
            else:
                st.info("Aucune donnée d'évolution disponible")

        else:
            st.warning("⚠️ Impossible de récupérer les statistiques globales")

        st.write("---")

    # --- ACTIONS ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        # Rigueur : On redirige vers la page de scan
        if st.button("📸 Nouveau Scan Santé"):
            st.switch_page("pages/scan.py") # Assure-toi de créer ce fichier !
            
    with c2:
        # Logique PDF simplifiée (on pourra l'affiner avec ton endpoint PDF)
        if st.button("📄 Historique des analyses"):
            st.info("🔄 Connexion au service d'impression...")
            st.switch_page("pages/historique.py")

            # Ici on fera l'appel vers ton Flask qui génère le PDF
            
    with c3:
        if st.button("🚪 Déconnexion", help="Quitter la session en toute sécurité"):
            st.session_state['token'] = None
            st.query_params.clear()
            st.switch_page("pages/auth.py")
else:
    st.error("❌ Erreur de récupération des données. Vérifiez que le Backend est lancé.")
    if st.button("🔄 Réessayer"):
        st.rerun()