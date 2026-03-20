import streamlit as st
import requests
import time
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

# --- QUOTA DE SCAN ---

def get_scan_quota():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        res = requests.get(f"{API_URL}/api/v1/scan/quota", headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None


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

st.set_page_config(page_title="Scan Santé - AgriLink", layout="centered")
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        .stCamera > div > div > button { background-color: #2ECC71 !important; }

        /* Style pour les recommandations */
        .recommendation-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #28a745;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .option-chimique {
            border-left-color: #dc3545;
            background-color: #fff5f5;
        }

        .option-biologique {
            border-left-color: #28a745;
            background-color: #f0f8f0;
        }

        .option-title {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
        }

        .produit-info {
            background-color: #e9ecef;
            padding: 8px;
            border-radius: 5px;
            margin: 5px 0;
            font-family: monospace;
        }

        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📸 Diagnostic Santé IA")
st.write("Prenez une photo d'une feuille ou d'une plante pour analyser sa santé.")

# --- QUOTA D'USAGE ---
scan_quota = get_scan_quota()
scan_disabled = False
scan_block_message = None

if scan_quota:
    used = scan_quota.get('daily_used', 0)
    limit = scan_quota.get('daily_limit', 10)
    remaining = scan_quota.get('daily_remaining', limit - used)

    st.info(f"📸 Scans aujourd'hui : {used}/{limit} — Restants : {remaining}")

    blocked_until = scan_quota.get('blocked_until')
    if blocked_until:
        from datetime import datetime
        remaining_sec = int(blocked_until - datetime.utcnow().timestamp())
        if remaining_sec < 0:
            remaining_sec = 0
        minutes = max(1, (remaining_sec + 59) // 60)
        scan_disabled = True
        scan_block_message = f"⚠️ Vous avez effectué {scan_quota.get('burst_limit', 3)} scans d'affilée. Attendez {minutes} min avant de relancer."

    elif remaining <= 0:
        scan_disabled = True
        scan_block_message = "⚠️ Quota quotidien atteint. Revenez demain pour de nouveaux scans."

    if scan_block_message:
        st.warning(scan_block_message)

# --- NAVIGATION ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⬅️ Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
with col2:
    if st.button("📜 Historique", use_container_width=True):
        st.switch_page("pages/historique.py")
with col3:
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state['token'] = None
        st.query_params.clear()
        st.switch_page("pages/auth.py")

st.write("---")

# --- CAPTURE IMAGE ---
# On propose deux options : Caméra en direct ou Upload
source = st.radio("Source de l'image :", ["Appareil Photo", "Importer un fichier"])

img_file = None
if source == "Appareil Photo":
    img_file = st.camera_input("Scanner la plante")
else:
    img_file = st.file_uploader("Choisir une image", type=["jpg", "jpeg", "png"])

if img_file:
    st.image(img_file, caption="Image prête pour analyse", use_container_width=True)
    
    if scan_disabled:
        st.warning(scan_block_message or "Vous ne pouvez pas lancer de scan pour le moment.")
    else:
        if st.button("🔍 Lancer l'analyse IA"):
            with st.spinner("Analyse en cours par Gemini..."):
                try:
                    # Préparation du fichier pour l'envoi
                    files = {"photo": (img_file.name, img_file.getvalue(), img_file.type)}
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

                    # Envoi au Backend (Route : /api/v1/scan)
                    res = requests.post(
                        f"{API_URL}/api/v1/scan",
                        headers=headers,
                        files=files,
                        timeout=30  # Gemini peut mettre un peu de temps
                    )

                    if res.status_code == 200:
                        data = res.json()

                        st.success("✅ Analyse terminée !")

                        # --- AFFICHAGE DES RÉSULTATS ---
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("🔍 Diagnostic")
                            status = data.get('statut_sante', 'Inconnu')
                            diagnostic = data.get('diagnostic_precis', 'Aucun diagnostic généré.')
                            facteur_sante = data.get('facteur_sante', 'N/A')
                            confiance = data.get('confiance_diagnostic', 'N/A')

                            # Couleur selon le statut
                            if status.upper() == "SAIN":
                                color = "#28a745"
                                emoji = "✅"
                            elif status.upper() == "MALADE":
                                color = "#dc3545"
                                emoji = "🚨"
                            else:
                                color = "#ffc107"
                                emoji = "⚠️"

                            st.markdown(f"**{emoji} Statut de santé :** <span style='color:{color};font-weight:bold;font-size:18px;'>{status}</span>", unsafe_allow_html=True)
                            st.markdown(f"**📊 Niveau de santé :** {facteur_sante}/1 ({int(float(facteur_sante)*100) if facteur_sante != 'N/A' else 'N/A'}%)")
                            st.markdown(f"**🎯 Confiance du diagnostic :** {confiance}")
                            st.markdown("---")
                            st.markdown(f"**💬 Diagnostic détaillé :**\n\n{diagnostic}")

                        with col2:
                            st.subheader("🩺 Action Recommandée")

                            # Récupération du protocole d'intervention
                            protocole = data.get('protocole_intervention', {})

                            if isinstance(protocole, dict) and protocole:
                                # Option A : Chimique
                                if 'option_A_chimique' in protocole:
                                    option_a = protocole['option_A_chimique']
                                    st.markdown("""
                                    <div class="recommendation-card option-chimique">
                                        <div class="option-title">🧪 Option A : Traitement Chimique</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    if 'produit_actif' in option_a:
                                        st.markdown(f"**Produit actif :** `{option_a['produit_actif']}`")
                                    if 'dosage_recommande' in option_a:
                                        st.markdown(f"**Dosage recommandé :** `{option_a['dosage_recommande']}`")

                                # Option B : Biologique
                                if 'option_B_biologique' in protocole:
                                    option_b = protocole['option_B_biologique']
                                    st.markdown("""
                                    <div class="recommendation-card option-biologique">
                                        <div class="option-title">🌱 Option B : Traitement Biologique</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    if 'produit_actif' in option_b:
                                        st.markdown(f"**Produit actif :** `{option_b['produit_actif']}`")
                                    if 'dosage_recommande' in option_b:
                                        st.markdown(f"**Dosage recommandé :** `{option_b['dosage_recommande']}`")

                                # Avertissement général
                                st.markdown("""
                                <div class="warning-box">
                                    <strong>⚠️ Important :</strong> Ces recommandations sont générées par IA.
                                    Consultez toujours un agronome ou un expert local avant application.
                                </div>
                                """, unsafe_allow_html=True)

                            else:
                                # Si pas de protocole structuré, afficher le texte brut
                                protocole_texte = str(protocole) if protocole else "Aucune recommandation générée."
                                st.markdown(f"**Protocole d'intervention :** {protocole_texte}")

                            # Bouton pour sauvegarder l'analyse
                            if st.button("💾 Sauvegarder cette analyse", use_container_width=True):
                                st.success("✅ Analyse sauvegardée dans votre historique !")
                                time.sleep(1)
                                st.rerun()

                    elif res.status_code == 422:
                        # Erreur de qualité d'image
                        try:
                            error_data = res.json()
                            st.warning("📷 **Image rejetée**")
                            st.info(error_data.get('message', 'La qualité de l\'image n\'est pas suffisante pour une analyse fiable.'))
                        except:
                            st.warning("📷 **Image rejetée** - Qualité insuffisante")

                    elif res.status_code == 503:
                        # Service temporairement indisponible (haute demande Gemini)
                        try:
                            error_data = res.json()
                            st.error("⏳ **Service temporairement indisponible**")
                            st.info(error_data.get('message', 'Le service d\'analyse IA est actuellement très sollicité.'))
                            retry_after = error_data.get('retry_after', 300)
                            minutes = retry_after // 60
                            st.info(f"⏰ **Réessayez dans {minutes} minute{'s' if minutes > 1 else ''}.**")
                        except:
                            st.error("⏳ **Service IA indisponible** - Réessayez plus tard")

                        # Bouton retry
                        if st.button("🔄 Réessayer maintenant", use_container_width=True):
                            st.rerun()

                    elif res.status_code == 429:
                        # Quota dépassé
                        try:
                            error_data = res.json()
                            st.error("📊 **Limite d'utilisation atteinte**")
                            st.info(error_data.get('message', 'Vous avez atteint la limite d\'utilisation du service.'))
                            retry_after = error_data.get('retry_after', 3600)
                            hours = retry_after // 3600
                            st.info(f"⏰ **Réessayez dans {hours} heure{'s' if hours > 1 else ''}.**")
                        except:
                            st.error("📊 **Quota dépassé** - Réessayez plus tard")

                    elif res.status_code == 502:
                        # Erreur de service IA
                        try:
                            error_data = res.json()
                            st.error("🤖 **Erreur du service d'analyse**")
                            st.info(error_data.get('message', 'Le service IA rencontre un problème temporaire.'))
                        except:
                            st.error("🤖 **Erreur service IA** - Problème temporaire")

                        if st.button("🔄 Réessayer", use_container_width=True):
                            st.rerun()

                    else:
                        # Erreur générique
                        try:
                            error_data = res.json()
                            error_type = error_data.get('error', 'INCONNU')
                            error_msg = error_data.get('message', 'Erreur inconnue')

                            if error_type == "ERREUR_BASE_DONNEES":
                                st.error("💾 **Erreur de sauvegarde**")
                                st.info("L'analyse a été effectuée mais n'a pas pu être enregistrée. Contactez le support si le problème persiste.")
                            elif error_type == "ERREUR_SAUVEGARDE_FICHIER":
                                st.warning("📁 **Erreur de sauvegarde image**")
                                st.info("L'analyse a été effectuée mais l'image n'a pas pu être sauvegardée.")
                            else:
                                st.error(f"❌ **Erreur ({res.status_code})**")
                                st.info(error_msg)

                        except:
                            # Si la réponse n'est pas du JSON
                            st.error(f"❌ **Erreur Backend ({res.status_code})**")
                            st.info("Une erreur inattendue s'est produite. Veuillez réessayer.")

                except Exception as e:
                    st.error("🌐 **Erreur de connexion**")
                    st.info("Impossible de contacter le serveur. Vérifiez votre connexion internet et réessayez.")
                    st.code(f"Détails: {str(e)}")

# --- PIED DE PAGE ---
st.markdown("---")
with st.expander("ℹ️ **Informations sur les erreurs possibles**"):
    st.markdown("""
    **🔄 Service temporairement indisponible (503)** : Le service IA est très sollicité. Patientez quelques minutes.

    **📊 Limite d'utilisation atteinte (429)** : Vous avez fait trop d'analyses récemment. Revenez dans 1 heure.

    **🤖 Erreur du service IA (502)** : Problème technique temporaire. Réessayez plus tard.

    **📷 Image rejetée (422)** : La photo n'est pas assez nette ou ne contient pas de plante visible.

    **💾 Erreur de sauvegarde** : L'analyse fonctionne mais les données n'ont pas été enregistrées.
    """)

st.caption("AgriLink IA utilise Gemini 2.5 Flash pour des diagnostics rapides et précis.")
