#!/usr/bin/env python3
"""
Script pour définir un utilisateur comme administrateur
Utilisation: python set_admin.py <email_utilisateur>
"""

import sys
import os

# Ajouter le répertoire Backend au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

from models.config import db, Parcelle, app_context
from app import app

def set_admin_user(email):
    """Définit un utilisateur comme administrateur"""
    with app.app_context():
        try:
            user = Parcelle.query.filter_by(email=email).first()
            if not user:
                print(f"❌ Utilisateur avec l'email '{email}' non trouvé.")
                return False

            user.role = 'admin'
            db.session.commit()

            print(f"✅ L'utilisateur '{user.nom}' ({email}) est maintenant administrateur.")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la mise à jour : {str(e)}")
            return False

def list_users():
    """Liste tous les utilisateurs"""
    with app.app_context():
        try:
            users = Parcelle.query.all()
            print("📋 Liste des utilisateurs :")
            print("-" * 60)
            for user in users:
                role_icon = "👑" if user.role == 'admin' else "👤"
                print(f"{role_icon} {user.nom} - {user.email} - Rôle: {user.role}")
            print("-" * 60)
        except Exception as e:
            print(f"❌ Erreur : {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python set_admin.py list                    # Lister tous les utilisateurs")
        print("  python set_admin.py <email>                 # Définir un utilisateur comme admin")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_users()
    else:
        email = command
        set_admin_user(email)