#!/usr/bin/env python3
"""
Script de migration pour ajouter les nouvelles tables Analytics et PasswordReset
Exécutez ce script une fois pour mettre à jour la base de données
"""

import sys
import os

# Ajouter le répertoire Backend au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

from models.config import db, app_context
from app import app

def run_migration():
    """Exécute la migration pour créer les nouvelles tables"""
    with app.app_context():
        try:
            print("🔄 Création des nouvelles tables...")

            # Création des tables Analytics et PasswordReset
            db.create_all()

            print("✅ Migration terminée avec succès !")
            print("📊 Nouvelles tables créées :")
            print("   - analytics (pour les statistiques d'utilisation)")
            print("   - password_resets (pour la réinitialisation de mot de passe)")

        except Exception as e:
            print(f"❌ Erreur lors de la migration : {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()