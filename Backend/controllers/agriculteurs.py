from app import app
from services.authentificate import AgriculteurModels
from middleware.authentificator import authentificate_required
from flask import request, jsonify, send_file, make_response
from models.config import db, Parcelle, Scan
from datetime import datetime
import io


model=AgriculteurModels()

@app.route('/api/v1/register',methods=['POST'])
def register():
    """
    Inscription d'un nouvel agriculteur et de sa parcelle.
    ---
    tags:
      - Authentification
    parameters:
      - name: nom
        in: formData
        type: string
        required: true
      - name: phone
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
      - name: culture_type
        in: formData
        type: string
        required: true
      - name: coords
        in: formData
        type: string
        description: Liste JSON des coordonnées [[lat, lon], ...]
        required: true
    responses:
      200:
        description: Inscription réussie
        schema:
          properties:
            msg:
              type: string
              example: "Inscription réussie"
      400:
        description: "Erreur dans les données envoyées (ex: pas assez de points GPS)"
    """
    return model.register()

@app.route('/api/v1/login',methods=['POST'])
def login():
    """
    Connexion de l'agriculteur pour obtenir un jeton d'accès.
    ---
    tags:
      - Authentification
    parameters:
      - name: phone
        in: formData
        type: string
        required: true
        description: Numéro de téléphone de l'agriculteur.
      - name: password
        in: formData
        type: string
        required: true
        description: Mot de passe du compte.
    responses:
      200:
        description: Connexion réussie, renvoie le token JWT.
        schema:
          properties:
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      401:
        description: Identifiants incorrects (Mot de passe faux ou utilisateur inconnu).
        schema:
          properties:
            message:
              type: string
              example: "Identifiants incorrects"
    """
    return model.login()


@app.route('/api/v1/scan',methods=['POST'])
@authentificate_required
def scan(current_user):
    """
        Analyse la santé d'une plante via une photo (IA Gemini).
        ---
        tags:
          - Analyse Santé
        security:
          - Bearer: []
        parameters:
          - name: photo
            in: formData
            type: file
            required: true
            description: Image de la plante à analyser (JPEG/PNG).
        responses:
          200:
            description: Diagnostic généré avec succès.
            schema:
              properties:
                statut_sante:
                  type: string
                  example: "MALADE"
                diagnostic_precis:
                  type: string
                  example: "Présence de rouille du maïs sur les feuilles inférieures."
                facteur_sante:
                  type: number
                  example: 0.65
                protocole_intervention:
                  type: object
          422:
            description: "Erreur de qualité : Image inexploitable (floue ou pas de plante)."
          401:
            description: Token manquant ou invalide.
        """
    from services.gemini_ai import ScanModels
    model=ScanModels()
    return model.analyze_health(current_user)


@app.route('/api/v1/dashboard/certificat', methods=['GET'])
@authentificate_required # Ton décorateur qui injecte current_user (la Parcelle)
def generate_dashboard_pdf(current_user):
    """
    Génère et affiche le certificat de crédibilité agricole (PDF).
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Le certificat PDF généré dynamiquement.
        content:
          application/pdf:
            schema:
              type: string
              format: binary
      401:
        description: Token manquant ou invalide.
      500:
        description: Erreur lors de la génération du document.
    """
    from services.score import ScoreModels, PDFService
    try:
        # 1. Calcul du score à la volée (Rigueur : pas de stockage)
        score_engine = ScoreModels()
        global_score = score_engine.calculate_global_score(current_user)

        # 2. Récupérer le dernier diagnostic pour le bilan de santé
        dernier_scan = Scan.query.filter_by(parcelle_id=current_user.id)\
                                 .order_by(Scan.date_analyse.desc()).first()
        
        diagnostic_texte = "Aucun scan effectué pour le moment."
        if dernier_scan:
            diagnostic_texte = dernier_scan.diagnostic

        # 3. Génération du PDF via ton service
        pdf_service = PDFService()
        pdf_bytes = pdf_service.generate_certificat(
            user_data=current_user, 
            score=global_score, 
            dernier_diagnostic=diagnostic_texte
        )
        # Vérifie si c'est bien des bytes avant de continuer (Debug rigoureux)
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1') # Conversion de secours
        # 4. Préparation de la réponse "Inline" (Affichage sans téléchargement forcé)
        return_data = io.BytesIO()
        return_data.write(pdf_bytes) # On écrit les bytes dedans
        return_data.seek(0)
        return send_file(
            return_data,
            mimetype='application/pdf',
            as_attachment=True, # Crucial pour l'affichage direct
            download_name=f"Dashboard_AgriLink_{current_user.nom}.pdf"
        )

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la génération du dashboard : {str(e)}"}), 500

@app.route('/api/v1/dashboard/stats', methods=['GET'])
@authentificate_required
def get_dashboard_stats(current_user):
    """
    Récupère les statistiques globales et l'historique pour le tableau de bord.
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Données du dashboard récupérées avec succès.
        schema:
          properties:
            agriculteur:
              type: string
              example: "Will Loïc"
            culture:
              type: string
              example: "Maïs"
            score:
              type: integer
              example: 72
            total_scans:
              type: integer
              example: 5
            historique:
              type: array
              items:
                properties:
                  date:
                    type: string
                    example: "12/03/2026"
                  statut:
                    type: string
                    example: "SAIN"
                  facteur:
                    type: number
                    example: 0.95
                  diagnostic:
                    type: string
                    example: "La plante est en excellente santé..."
      401:
        description: Non autorisé - Token invalide ou expiré.
    """
    from services.score import ScoreModels, PDFService
    try:
        # 1. Calcul du score global
        score_engine = ScoreModels()
        global_score = score_engine.calculate_global_score(current_user)

        # 1.1. Quotas de scan (pour affichage)
        from services.gemini_ai import _compute_scan_quota
        scan_quota = _compute_scan_quota(current_user)

        # 2. Récupération de l'historique des scans
        scans = Scan.query.filter_by(parcelle_id=current_user.id)\
                          .order_by(Scan.date_analyse.desc()).all()
        
        history = []
        for s in scans:
            history.append({
                "date": s.date_analyse.strftime("%d/%m/%Y"),
                "statut": s.statut_sante,
                "facteur": s.facteur_sante,
                "diagnostic": s.diagnostic[:100] + "..." # On tronque pour la liste
            })

        # 3. Réponse JSON propre
        return jsonify({
            "agriculteur": current_user.nom,
            "culture": current_user.culture_type,
            "score": global_score,
            "total_scans": len(scans),
            "historique": history,
            "scan_quota": scan_quota
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/scan/quota', methods=['GET'])
@authentificate_required
def get_scan_quota(current_user):
    """Retourne l'état de quota de scan pour l'utilisateur connecté."""
    from services.gemini_ai import _compute_scan_quota
    quota = _compute_scan_quota(current_user)
    return jsonify(quota), 200


# --- NOUVELLES FONCTIONNALITÉS ---

@app.route('/api/v1/forgot-password', methods=['POST'])
def forgot_password():

    """
    Demande de réinitialisation de mot de passe.
    ---
    tags:
      - Authentification
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: Email de l'utilisateur
    responses:
      200:
        description: Email de réinitialisation envoyé
      500:
        description: Erreur serveur
    """
    from services.password_reset import PasswordResetService
    service = PasswordResetService()

    email = request.form.get('email')
    if not email:
        return jsonify({"error": "Email requis"}), 400

    # On récupère le résultat du service (qui est un tuple)
    result, status_code = service.request_password_reset(email)
    
    # ON FORCE LE JSON ICI
    return jsonify(result), status_code


@app.route('/api/v1/reset-password', methods=['POST'])
def reset_password():
    """
    Réinitialisation du mot de passe avec token.
    ---
    tags:
      - Authentification
    parameters:
      - name: token
        in: formData
        type: string
        required: true
        description: Token de réinitialisation
      - name: new_password
        in: formData
        type: string
        required: true
        description: Nouveau mot de passe
    responses:
      200:
        description: Mot de passe réinitialisé
      400:
        description: Token invalide ou expiré
      500:
        description: Erreur serveur
    """
    from services.password_reset import PasswordResetService
    service = PasswordResetService()

    token = request.form.get('token')
    print(token) # Debug rigoureux
    new_password = request.form.get('new_password')

    if not token or not new_password:
        return jsonify({"error": "Token et nouveau mot de passe requis"}), 400

    return service.reset_password(token, new_password)


@app.route('/api/v1/analytics', methods=['GET'])
@authentificate_required
def get_analytics(current_user):
    """
    Récupère les statistiques d'utilisation (réservé aux admins).
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Statistiques récupérées
      403:
        description: Accès non autorisé
    """
    # Vérification du rôle administrateur
    if current_user.role != 'admin':
        return jsonify({"error": "Accès réservé aux administrateurs"}), 403

    from services.password_reset import AnalyticsService
    service = AnalyticsService()

    analytics_data = service.get_analytics_summary()
    return jsonify(analytics_data), 200


@app.route('/api/v1/user/profile', methods=['GET'])
@authentificate_required
def get_user_profile(current_user):
    """
    Récupère le profil de l'utilisateur connecté.
    ---
    tags:
      - Utilisateur
    security:
      - Bearer: []
    responses:
      200:
        description: Profil récupéré avec succès
        schema:
          properties:
            id:
              type: integer
            nom:
              type: string
            email:
              type: string
            role:
              type: string
            culture_type:
              type: string
    """
    return jsonify({
        "id": current_user.id,
        "nom": current_user.nom,
        "email": current_user.email,
        "role": current_user.role,
        "culture_type": current_user.culture_type
    }), 200


# --- ADMINISTRATION (réservé aux admins) ---

@app.route('/api/v1/admin/users', methods=['GET'])
@authentificate_required
def get_all_users(current_user):
    """
    Récupère la liste de tous les utilisateurs (admin uniquement).
    ---
    tags:
      - Administration
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des utilisateurs récupérée
      403:
        description: Accès non autorisé
    """
    # Vérification du rôle administrateur
    if current_user.role != 'admin':
        return jsonify({"error": "Accès réservé aux administrateurs"}), 403

    try:
        users = Parcelle.query.all()
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "nom": user.nom,
                "email": user.email,
                "phone": user.phone,
                "culture_type": user.culture_type,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })

        return jsonify(users_data), 200

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des utilisateurs: {str(e)}"}), 500


@app.route('/api/v1/admin/promote/<int:user_id>', methods=['POST'])
@authentificate_required
def promote_user(current_user, user_id):
    """
    Promouvoir un utilisateur au rang d'administrateur.
    ---
    tags:
      - Administration
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Utilisateur promu
      403:
        description: Accès non autorisé
      404:
        description: Utilisateur non trouvé
    """
    # Vérification du rôle administrateur
    if current_user.role != 'admin':
        return jsonify({"error": "Accès réservé aux administrateurs"}), 403

    try:
        user = Parcelle.query.get(user_id)
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        user.role = 'admin'
        db.session.commit()

        return jsonify({"message": f"{user.nom} est maintenant administrateur"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la promotion: {str(e)}"}), 500


@app.route('/api/v1/admin/demote/<int:user_id>', methods=['POST'])
@authentificate_required
def demote_user(current_user, user_id):
    """
    Rétrograder un administrateur en utilisateur normal.
    ---
    tags:
      - Administration
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Utilisateur rétrogradé
      403:
        description: Accès non autorisé
      404:
        description: Utilisateur non trouvé
    """
    # Vérification du rôle administrateur
    if current_user.role != 'admin':
        return jsonify({"error": "Accès réservé aux administrateurs"}), 403

    # Empêcher l'auto-rétrogradation
    if current_user.id == user_id:
        return jsonify({"error": "Vous ne pouvez pas vous rétrograder vous-même"}), 400

    try:
        user = Parcelle.query.get(user_id)
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        user.role = 'user'
        db.session.commit()

        return jsonify({"message": f"{user.nom} n'est plus administrateur"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la rétrogradation: {str(e)}"}), 500
