import streamlit as st

# --- CONFIGURATION PAGE ---

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

st.set_page_config(
    page_title="AgriLink - Révolutionnez votre agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLES CSS ---
st.markdown("""
    <style>
        /* Masquer la barre de navigation latérale */
        [data-testid="stSidebarNav"] { display: none; }

        /* Styles généraux */
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Header */
        .hero-header {
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin: 20px 0;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .hero-title {
            font-size: 3.5em;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .hero-subtitle {
            font-size: 1.4em;
            margin-bottom: 30px;
            opacity: 0.9;
        }

        /* Cartes de fonctionnalités */
        .feature-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-left: 5px solid #28a745;
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        }

        .feature-icon {
            font-size: 3em;
            margin-bottom: 20px;
        }

        .feature-title {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .feature-description {
            color: #7f8c8d;
            line-height: 1.6;
        }

        /* Section CTA */
        .cta-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 50px 30px;
            text-align: center;
            margin: 40px 0;
            color: white;
        }

        .cta-title {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .cta-subtitle {
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }

        /* Boutons */
        .btn-primary {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
            padding: 12px 35px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        /* Statistiques */
        .stats-section {
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin: 40px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }

        .stat-item {
            text-align: center;
            margin: 20px 0;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #7f8c8d;
            font-size: 1.1em;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 30px;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
            margin-top: 50px;
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER HERO ---
st.markdown("""
    <div class="hero-header fade-in-up">
        <div class="hero-title">🌱 AgriLink</div>
        <div class="hero-subtitle">Révolutionnez votre agriculture avec l'intelligence artificielle</div>
        <p style="font-size: 1.1em; margin-bottom: 30px;">
            Analysez la santé de vos cultures en temps réel, obtenez des recommandations personnalisées
            et améliorez vos rendements grâce à notre technologie IA de pointe.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- BOUTONS D'ACTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Commencer maintenant", use_container_width=True, type="primary"):
        st.switch_page("pages/auth.py")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔐 J'ai déjà un compte", use_container_width=True):
        st.switch_page("pages/auth.py")
    st.markdown("<br>", unsafe_allow_html=True)

    # Section "En savoir plus" (expandable)
    with st.expander("📖 En savoir plus sur AgriLink"):
        st.markdown("""
        ### 🌟 Découvrez AgriLink

        AgriLink est la première plateforme agricole qui utilise l'intelligence artificielle
        pour analyser la santé de vos cultures en quelques secondes.

        **Comment ça marche ?**
        1. 📸 Prenez une photo de votre plante
        2. 🤖 Notre IA analyse l'état de santé
        3. 💊 Recevez des recommandations de traitement
        4. 📊 Suivez l'évolution dans votre tableau de bord

        **Avantages :**
        - ✅ Diagnostic instantané et précis
        - ✅ Recommandations personnalisées
        - ✅ Suivi historique complet
        - ✅ Interface simple et intuitive
        - ✅ Support technique 24/7
        """)
# --- FONCTIONNALITÉS ---
st.markdown("## ✨ Fonctionnalités principales")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📸</div>
        <div class="feature-title">Analyse par photo</div>
        <div class="feature-description">
            Prenez simplement une photo de votre plante avec votre smartphone.
            Notre IA analyse automatiquement les signes de maladie, parasites et carences.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🩺</div>
        <div class="feature-title">Diagnostic instantané</div>
        <div class="feature-description">
            Recevez un diagnostic précis en quelques secondes avec un niveau de
            confiance et des recommandations de traitement adaptées à votre culture.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Suivi historique</div>
        <div class="feature-description">
            Gardez un historique complet de vos analyses et suivez l'évolution
            de la santé de vos parcelles au fil du temps.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- STATISTIQUES ---
st.markdown("""
    <div class="stats-section">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 40px;">
            🌍 Impact d'AgriLink
        </h2>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-item">
        <div class="stat-number">500+</div>
        <div class="stat-label">Agriculteurs actifs</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-item">
        <div class="stat-number">10K+</div>
        <div class="stat-label">Analyses réalisées</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-item">
        <div class="stat-number">95%</div>
        <div class="stat-label">Précision diagnostic</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-item">
        <div class="stat-number">24h</div>
        <div class="stat-label">Support technique</div>
    </div>
    """, unsafe_allow_html=True)

# --- SECTION CTA ---
st.markdown("""
    <div class="cta-section">
        <div class="cta-title">Prêt à révolutionner votre agriculture ?</div>
        <div class="cta-subtitle">
            Rejoignez des milliers d'agriculteurs qui ont déjà adopté AgriLink
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🌱 Créer mon compte gratuit", use_container_width=True, type="primary"):
        st.switch_page("pages/auth.py")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔓 Se connecter", use_container_width=True):
        st.switch_page("pages/auth.py")

# --- CULTURES SUPPORTÉES ---
st.markdown("## 🌾 Cultures supportées")

cultures = ["Maïs", "Riz", "Cacao", "Café", "Manioc", "Tomates", "Pommes de terre", "Blé", "Soja", "Arachide"]
cols = st.columns(5)

for i, culture in enumerate(cultures):
    with cols[i % 5]:
        st.markdown(f"""
        <div style="background: white; padding: 15px; color: black; border-radius: 10px; margin: 5px 0;
                    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            🌱 {culture}
        </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        <p><strong>AgriLink</strong> - Révolutionnez votre agriculture avec l'IA</p>
        <p style="font-size: 0.9em;">
            🏢 Siège social | 📧 willloic36@gmail.com | 📞 +237 692 25 34 74
        </p>
        <p style="font-size: 0.8em; margin-top: 20px;">
            © 2026 AgriLink. Tous droits réservés. | Conditions générales | Politique de confidentialité
        </p>
    </div>
""", unsafe_allow_html=True)
