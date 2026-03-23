import os
import secrets
from datetime import datetime, timedelta
from flask import current_app
from models.config import db, Parcelle, Analytics, PasswordReset, Scan
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models.config import mail

bcrypt = Bcrypt()

class PasswordResetService:
    def __init__(self):
        #self.mail = Mail(current_app)
        pass

    def generate_reset_token(self):
        """Génère un token sécurisé pour la réinitialisation"""
        return secrets.token_urlsafe(32)

    def send_reset_email(self, email, reset_token):
        """Envoie un email de réinitialisation de mot de passe"""
        
        try:
            base_url = os.getenv('FRONTEND_URL', 'http://localhost:8501')
            reset_url = f"{base_url}/reset_password?token={reset_token}"

            msg = Message(
                subject='Réinitialisation de votre mot de passe AgriLink',
                sender=os.getenv('MAIL_USERNAME'),
                recipients=[email]
            )

            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1>🔐 Réinitialisation de mot de passe</h1>
                    <p>AgriLink - Analyse Agricole IA</p>
                </div>

                <div style="background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px;">
                    <h2>Bonjour,</h2>

                    <p>Vous avez demandé la réinitialisation de votre mot de passe sur la plateforme AgriLink.</p>

                    <p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            🔑 Réinitialiser mon mot de passe
                        </a>
                    </div>

                    <p><strong>⚠️ Important :</strong> Ce lien expirera dans 1 heure pour des raisons de sécurité.</p>

                    <p>Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.</p>

                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                    <p style="color: #666; font-size: 12px;">
                        Cordialement,<br>
                        L'équipe AgriLink<br>
                        🌱 Analyse agricole intelligente
                    </p>
                </div>
            </body>
            </html>
            """

            #mail.send(msg)
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False

    def request_password_reset(self, email):
        """Demande de réinitialisation de mot de passe"""
        try:
            # Vérifier si l'utilisateur existe
            user = Parcelle.query.filter_by(email=email).first()
            if not user:
                return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."}, 200

            # Générer le token
            reset_token = self.generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Sauvegarder le token en base
            password_reset = PasswordReset(
                parcelle_id=user.id,
                reset_token=reset_token,
                expires_at=expires_at
            )
            db.session.add(password_reset)
            db.session.commit()

            # Envoyer l'email
            if self.send_reset_email(email, reset_token):
                return {"message": "Un email de réinitialisation a été envoyé."}, 200
            else:
                return {"error": "Erreur lors de l'envoi de l'email."}, 500

        except Exception as e:
            db.session.rollback()
            return {"error": f"Erreur lors de la demande de réinitialisation: {str(e)}"}, 500

    def reset_password(self, token, new_password):
        """Réinitialise le mot de passe avec le token"""
        try:
            # Vérifier le token
            password_reset = PasswordReset.query.filter_by(
                reset_token=token,
                used=False
            ).first()
            print("password_reset", password_reset)
            if not password_reset:
                return {"error": "Token invalide ou expiré."}, 400

            if password_reset.expires_at < datetime.utcnow():
                return {"error": "Token expiré."}, 400

            # Récupérer l'utilisateur
            user = Parcelle.query.get(password_reset.parcelle_id)
            if not user:
                return {"error": "Utilisateur non trouvé."}, 404

            # Mettre à jour le mot de passe
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            password_reset.used = True

            db.session.commit()

            return {"message": "Mot de passe réinitialisé avec succès."}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": f"Erreur lors de la réinitialisation: {str(e)}"}, 500


class AnalyticsService:
    def log_event(self, event_type, parcelle_id=None, details=None):
        """Enregistre un événement dans les analytics"""
        try:
            analytics = Analytics(
                event_type=event_type,
                parcelle_id=parcelle_id,
                details=details or {}
            )
            db.session.add(analytics)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du logging analytics: {str(e)}")

    def get_analytics_summary(self):
        """Récupère un résumé des analytics"""
        try:
            from sqlalchemy import func

            # Statistiques générales
            total_users = Parcelle.query.count()
            total_scans = Scan.query.count()

            # Statistiques par période (derniers 30 jours)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            recent_logins = Analytics.query.filter(
                Analytics.event_type == 'login',
                Analytics.timestamp >= thirty_days_ago
            ).count()

            recent_scans = Analytics.query.filter(
                Analytics.event_type == 'scan',
                Analytics.timestamp >= thirty_days_ago
            ).count()

            recent_registrations = Analytics.query.filter(
                Analytics.event_type == 'register',
                Analytics.timestamp >= thirty_days_ago
            ).count()

            # Répartition par culture
            culture_stats = db.session.query(
                Parcelle.culture_type,
                func.count(Parcelle.id).label('count')
            ).group_by(Parcelle.culture_type).all()

            # Évolution des scans sur les 7 derniers jours
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            daily_scans = db.session.query(
                func.date(Analytics.timestamp).label('date'),
                func.count(Analytics.id).label('count')
            ).filter(
                Analytics.event_type == 'scan',
                Analytics.timestamp >= seven_days_ago
            ).group_by(func.date(Analytics.timestamp)).all()

            return {
                "total_users": total_users,
                "total_scans": total_scans,
                "recent_activity": {
                    "logins_30_days": recent_logins,
                    "scans_30_days": recent_scans,
                    "registrations_30_days": recent_registrations
                },
                "culture_distribution": [
                    {"culture": stat.culture_type, "count": stat.count}
                    for stat in culture_stats
                ],
                "daily_scans_last_7_days": [
                    {"date": str(stat.date), "count": stat.count}
                    for stat in daily_scans
                ]
            }

        except Exception as e:
            return {"error": f"Erreur lors de la récupération des analytics: {str(e)}"}
