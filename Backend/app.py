import os
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
import click
from models.config import db, ma, app_context, setup_db
from datetime import datetime
from flasgger import Swagger


app = Flask(__name__)
CORS(app, origins="*")


#----------CONFIGURATIONS--------------

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/agrilink_db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY']='1234'
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')

# Configuration Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@agri-link.com')
print(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])  # Debug : vérifier les variables d'environnement
mail = Mail(app)

# Configuration simple de Swagger
app.config['SWAGGER'] = {
    'title': 'AgriLink API',
    'uiversion': 3,
    'description': 'Système de score de crédit agricole basé sur l\'analyse IA',
    'securityDefinitions': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Ajoutez votre token sous la forme : Bearer <votre_token>'
        }
    }
}

swagger = Swagger(app)
# --- INITIALISATION DES EXTENSIONS ---
setup_db(app)
db.init_app(app)  # C'est ici que la liaison se fait proprement
ma.init_app(app)
#with app.app_context():
app_context(app) # On lance tes corrections MySQL

from controllers import agriculteurs

# Commandes Flask CLI pour la gestion des admins
@app.cli.command("create-admin")
@click.argument("email")
def create_admin(email):
    #Créer un administrateur - Usage: flask create-admin user@example.com
    with app.app_context():
        from models.config import Parcelle, db

        user = Parcelle.query.filter_by(email=email).first()
        if not user:
            click.echo(f"❌ Utilisateur avec l'email '{email}' non trouvé.")
            return

        user.role = 'admin'
        db.session.commit()
        click.echo(f"✅ {user.nom} ({email}) est maintenant administrateur.")

@app.cli.command("list-users")
def list_users():
    #Lister tous les utilisateurs - Usage: flask list-users
    with app.app_context():
        from models.config import Parcelle

        users = Parcelle.query.all()
        click.echo("📋 Liste des utilisateurs :")
        click.echo("-" * 60)
        for user in users:
            role_icon = "👑" if user.role == 'admin' else "👤"
            click.echo(f"{role_icon} {user.nom} - {user.email} - Rôle: {user.role}")
        click.echo("-" * 60)

if __name__ == '__main__':
    #app.run()
    # Mode debug pour le développement
    app.run(debug=True, host='0.0.0.0', port=5000)


