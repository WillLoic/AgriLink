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

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")

# --- CONFIGURATION ---
st.set_page_config(page_title="Historique des analyses", layout="wide")
st.markdown("""
    <style>
        /* Masquer la barre de navigation latérale de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }

        /* Style pour les cartes d'historique */
        .history-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 5px solid #28a745;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: black;
        }

        .history-card.good {
            border-left-color: #28a745;
            background-color: #d4edda;
        }

        .history-card.warning {
            border-left-color: #ffc107;
            background-color: #fff3cd;
        }

        .history-card.danger {
            border-left-color: #dc3545;
            background-color: #f8d7da;
        }

        .history-card.rejected {
            border-left-color: #6c757d;
            background-color: #e2e3e5;
        }

        .score-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 14px;
        }

        .score-good { background-color: #28a745; color: white; }
        .score-warning { background-color: #ffc107; color: black; }
        .score-danger { background-color: #dc3545; color: white; }
        .score-rejected { background-color: #6c757d; color: white; }

        /* Style pour le tableau */
        .stDataFrame { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def get_status_color(statut):
    """Retourne la classe CSS selon le statut"""
    if statut == "BON":
        return "good"
    elif statut == "MOYEN":
        return "warning"
    elif statut == "MAUVAIS":
        return "danger"
    else:
        return "rejected"

def get_score_badge(facteur):
    """Retourne le badge de score avec couleur appropriée"""
    if facteur >= 0.70:
        return f'<span class="score-badge score-good">🌱 {facteur}% - Excellent</span>'
    elif facteur >= 0.50:
        return f'<span class="score-badge score-warning">⚠️ {facteur}% - Acceptable</span>'
    elif facteur >= 0.30:
        return f'<span class="score-badge score-danger">🚨 {facteur}% - Critique</span>'
    else:
        return f'<span class="score-badge score-rejected">❌ {facteur}% - Rejeté</span>'

# --- RÉCUPÉRATION DES DONNÉES ---
headers = {"Authorization": f"Bearer {st.session_state['token']}"}
res = requests.get(f"{API_URL}/api/v1/dashboard/stats", headers=headers, timeout=5)

if res.status_code == 200:
    stats = res.json()
    historique = stats.get('historique', [])
else:
    stats = None
    historique = []

# --- INTERFACE ---
st.title("📜 Historique des analyses")

# Statistiques générales
if stats:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total des analyses", f"{stats.get('total_scans', 0)}")
    with col2:
        score_global = stats.get('score', 0)
        st.metric("Score global", f"{score_global}/100")
    with col3:
        culture = stats.get('culture', 'N/A')
        st.metric("Culture", culture)

st.markdown("---")

# --- AFFICHAGE DE L'HISTORIQUE ---
if historique and len(historique) > 0:
    st.subheader("📋 Détail de vos analyses")

    # Vue en cartes (plus visuelle)
    st.markdown("### 🃏 Vue détaillée")
    for i, scan in enumerate(historique, 1):
        statut = scan.get('statut', 'INCONNU')
        facteur = scan.get('facteur', 0)
        date = scan.get('date', 'N/A')
        diagnostic = scan.get('diagnostic', 'Aucun diagnostic disponible')

        # Déterminer la classe CSS selon le statut
        card_class = get_status_color(statut)

        st.markdown(f"""
        <div class="history-card {card_class}">
            <h4>📅 Analyse #{i} - {date}</h4>
            <p><strong>Statut général:</strong> {statut}</p>
            <p><strong>Score de santé:</strong> {get_score_badge(facteur)}</p>
            <p><strong>Diagnostic:</strong> {diagnostic}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Vue en tableau (plus compacte)
    st.markdown("### 📊 Vue synthétique")

    # Préparer les données pour le tableau
    table_data = []
    for scan in historique:
        table_data.append({
            "📅 Date": scan.get('date', 'N/A'),
            "🏥 Statut": scan.get('statut', 'INCONNU'),
            "📊 Score": f"{scan.get('facteur', 0)}%",
            "🔍 Diagnostic": scan.get('diagnostic', 'N/A')[:50] + "..." if len(scan.get('diagnostic', '')) > 50 else scan.get('diagnostic', 'N/A')
        })

    if table_data:
        st.dataframe(table_data, use_container_width=True)

else:
    st.info("🌱 Aucune analyse réalisée pour le moment. Commencez par faire votre premier scan depuis le dashboard !")

# --- ACTIONS ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("📸 Nouvelle analyse", use_container_width=True):
        st.switch_page("pages/scan.py")

with col2:
    if st.button("⬅️ Retour au Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
