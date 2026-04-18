from PIL import Image
import io, json, os
from flask import request, jsonify
from models.config import Parcelle, db, Scan
from google import genai
from google.genai import types
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from app import app

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier uploads s'il n'existe pas
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Quotas de scan (par utilisateur)
DAILY_SCAN_LIMIT = 10
BURST_SCAN_LIMIT = 3
BURST_LOCK_MINUTES = 10

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
def _compute_scan_quota(current_user):
    """Calcule le quota de scans pour un utilisateur (quotidien + burst)."""
    now = datetime.utcnow()
    start_of_day = datetime(now.year, now.month, now.day)

    # Nombre de scans effectués dans la journée en cours
    daily_used = Scan.query.filter(
        Scan.parcelle_id == current_user.id,
        Scan.date_analyse >= start_of_day
    ).count()
    daily_remaining = max(0, DAILY_SCAN_LIMIT - daily_used)

    # Détection du burst : regarder les 3 derniers scans (toutes périodes confondues)
    last_three = Scan.query.filter(
        Scan.parcelle_id == current_user.id
    ).order_by(Scan.date_analyse.desc()).limit(BURST_SCAN_LIMIT).all()

    blocked_until = None
    if len(last_three) == BURST_SCAN_LIMIT:
        oldest_of_three = last_three[-1].date_analyse
        most_recent = last_three[0].date_analyse

        # Si les 3 scans ont été effectués dans une fenêtre de BURST_LOCK_MINUTES
        if (now - oldest_of_three) <= timedelta(minutes=BURST_LOCK_MINUTES):
            blocked_until = most_recent + timedelta(minutes=BURST_LOCK_MINUTES)
            if blocked_until <= now:
                blocked_until = None

    # Temps restant avant minuit (pour reset du quota journalier)
    tomorrow = start_of_day + timedelta(days=1)
    seconds_until_midnight = int((tomorrow - now).total_seconds())

    return {
        "daily_used": daily_used,
        "daily_limit": DAILY_SCAN_LIMIT,
        "daily_remaining": daily_remaining,
        "daily_reset_in_seconds": seconds_until_midnight,
        "burst_limit": BURST_SCAN_LIMIT,
        "burst_window_minutes": BURST_LOCK_MINUTES,
        "blocked_until": int(blocked_until.timestamp()) if blocked_until else None
    }


class ScanModels():
    def analyze_health(self,current_user):
        # 0. Vérification du quota (journée + burst)
        quota = _compute_scan_quota(current_user)

        if quota['daily_remaining'] <= 0:
            return jsonify({
                "error": "QUOTA_JOURNALIER_ATTEINT",
                "message": "Vous avez atteint le nombre maximum de scans autorisés aujourd'hui.",
                "daily_used": quota['daily_used'],
                "daily_limit": quota['daily_limit'],
                "retry_after": quota.get('daily_reset_in_seconds')
            }), 429

        if quota['blocked_until']:
            retry_after = int(quota['blocked_until'] - datetime.utcnow().timestamp())
            if retry_after < 0:
                retry_after = 0
            return jsonify({
                "error": "BURST_LIMIT_ATTEINT",
                "message": "Vous avez effectué trop de scans d'affilée. Réessayez dans quelques minutes.",
                "retry_after": retry_after
            }), 429

        # 1. Récupération des données
        file = request.files.get('photo')
        #lat_scan = float(request.form.get('lat'))
        #lng_scan = float(request.form.get('lng'))

        if file.filename == '' or not allowed_file(file.filename):
                return jsonify({"error": "Fichier invalide"}), 422
        
        # 2. Vérification de la parcelle (Rigueur)
        parcelle = Parcelle.query.get(current_user.id)
        if not parcelle:
            return jsonify({"error": "Parcelle non trouvée"}), 403
        # Ici, tu devrais ajouter une logique de vérification de distance
        # (ST_Distance en SQL ou calcul Haversine en Python)

        prompt = f"""
        Tu es un expert agronome spécialisé dans le diagnostic des plantes en contexte africain.
        Ta mission est d’analyser une image de plante et de fournir un diagnostic clair, fiable et directement exploitable.
        
        Étape 1 : ANALYSE DE QUALITÉ
        Vérifie si cette image est exploitable pour un diagnostic agronomique (Netteté, Luminosité, Présence de végétaux).
        Si l'image est floue, trop sombre, ou ne contient pas de plantes, renvoie UNIQUEMENT :
        {{"statut_sante": "REJETÉ", "diagnostic_precis": "Qualité image insuffisante : [RAISON]"}}

        Étape 2 : DIAGNOSTIC (Si qualité OK)
        Fais une analyse detaillée et approfondie de la photo de {parcelle.culture_type} .
        Tu es un expert en pathologie végétale.
        STRUCTURE JSON ATTENDUE :
        {{
            "statut_sante": "SAIN" ou "MALADE",
            "diagnostic_precis": "Diagnostic principal : ... | Symptômes : ... | Hypothèses secondaires : ... | Causes probables : ...",
            "confiance_diagnostic": "X%",
            "facteur_sante": float (entre 0.1 et 1.0),
            "protocole_intervention": {{
                "option_A_chimique": {{
                  "produit_actif": "nom du traitement recommandé",
                  "dosage_recommande": "quantité + fréquence + durée"
                }},
                "option_B_biologique": {{
                  "produit_actif": "solution naturelle ou locale",
                  "dosage_recommande": "méthode + fréquence"
    }}
            }}
        }} """
        

        
        img = file.read()
        try:
        
            # 3. Préparation de l'IA (Gemini)
            import time

            start_ia = time.time()
            
            # Appel avec le SDK moderne (Gemini 2.5 Flash)
            try:
                response = client.models.generate_content(
                        model="gemini-1.5-flash", #gemini-2.5-flash-Lite pour un plus grand quota mais des réponses moins détaillées
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=img, mime_type=file.content_type)
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                models = client.models.list()
                for model in models:
                    print(f'✅ {model.name} → ID: {model.id}')
            except Exception as api_error:
                # Gestion spécifique des erreurs Gemini
                error_str = str(api_error).lower()
                if "503" in error_str or "unavailable" in error_str or "high demand" in error_str:
                    return jsonify({
                        "error": "SERVICE_TEMPORAIREMENT_INDISPONIBLE",
                        "message": "Le service d'analyse IA est actuellement très sollicité. Veuillez réessayer dans quelques minutes.",
                        "details": "Erreur 503 - Service indisponible temporairement",
                        "retry_after": 300  # 5 minutes en secondes
                    }), 503
                elif "quota" in error_str or "rate limit" in error_str:
                    return jsonify({
                        "error": "QUOTA_DEPASSE",
                        "message": "Limite d'utilisation atteinte. Veuillez réessayer plus tard.",
                        "details": "Quota API dépassé",
                        "retry_after": 3600  # 1 heure en secondes
                    }), 429
                else:
                    # Erreur API générique
                    return jsonify({
                        "error": "ERREUR_SERVICE_IA",
                        "message": "Erreur temporaire du service d'analyse IA. Veuillez réessayer.",
                        "details": str(api_error)
                    }), 502

            #print(f"TEMPS IA SEULE : {time.time() - start_ia} secondes")

            # Vérification que la réponse contient du texte
            if not hasattr(response, 'text') or not response.text:
                return jsonify({
                    "error": "REPONSE_IA_INVALIDE",
                    "message": "Le service IA n'a pas pu analyser l'image. Veuillez réessayer avec une autre photo."
                }), 502

            # 4. Nettoyage du JSON (Gemini met parfois des ```json ...)
            try:
                # Parse direct (le mode JSON de Gemini garantit un JSON valide)
                diag_json = json.loads(response.text)
            except json.JSONDecodeError as json_error:
                return jsonify({
                    "error": "REPONSE_IA_INVALIDE",
                    "message": "Erreur de traitement de la réponse IA. Veuillez réessayer.",
                    "details": f"JSON invalide: {str(json_error)}"
                }), 502

                # Si l'IA a rejeté l'image
            if diag_json.get("statut_sante") == "REJETÉ":
                return jsonify({
                        "statut": "ERREUR_QUALITÉ",
                        "message": diag_json.get("diagnostic_precis")
                    }), 422
            # 5. Enregistrement du Scan
            nouveau_scan = Scan(
                parcelle_id=current_user.id,
                image_url="URL_CLOUDINARY_ICI", # Pour l'instant stocke le nom du fichier
                date_analyse=datetime.utcnow(),
                statut_sante=diag_json.get('statut_sante'),
                diagnostic=diag_json.get('diagnostic_precis'),
                facteur_sante=diag_json.get('facteur_sante'),
                protocole_json=diag_json.get('protocole_intervention')
            )
            
            db.session.add(nouveau_scan)
            db.session.commit()
            

            # Logger l'événement de scan
            from services.password_reset import AnalyticsService
            analytics = AnalyticsService()
            analytics.log_event('scan', current_user.id, {
                'statut_sante': diag_json.get('statut_sante'),
                'facteur_sante': diag_json.get('facteur_sante'),
                'culture_type': parcelle.culture_type
            })

            # Sauvegarde sécurisée
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file.seek(0)
            filename = secure_filename(f"P{parcelle.id}_{timestamp}.jpg")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify(diag_json), 200

        except json.JSONDecodeError as json_error:
            db.session.rollback()
            return jsonify({
                "error": "ERREUR_TRAITEMENT",
                "message": "Erreur lors du traitement de la réponse IA.",
                "details": str(json_error)
            }), 500

        except Exception as e:
            db.session.rollback()
            error_str = str(e).lower()

            # Gestion des erreurs de base de données
            if "mysql" in error_str or "database" in error_str:
                return jsonify({
                    "error": "ERREUR_BASE_DONNEES",
                    "message": "Erreur de sauvegarde des données. L'analyse a été effectuée mais n'a pas pu être enregistrée.",
                    "details": "Problème de base de données"
                }), 500

            # Gestion des erreurs de fichier
            elif "file" in error_str or "upload" in error_str:
                return jsonify({
                    "error": "ERREUR_SAUVEGARDE_FICHIER",
                    "message": "Erreur lors de la sauvegarde de l'image. L'analyse a été effectuée.",
                    "details": "Problème de stockage fichier"
                }), 500

            # Erreur générique
            else:
                return jsonify({
                    "error": "ERREUR_INATTENDUE",
                    "message": "Une erreur inattendue s'est produite. Veuillez réessayer.",
                    "details": str(e)
                }), 500
