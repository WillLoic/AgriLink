from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_marshmallow import Marshmallow
from datetime import datetime
from sqlalchemy import Column, Integer, String, text, func
from sqlalchemy.types import UserDefinedType
from flask_bcrypt import Bcrypt
import os


uri = os.getenv("SQLALCHEMY_DATABASE_URI")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

db=SQLAlchemy()
ma = Marshmallow()

bcrypt=Bcrypt()
"""class Agriculteurs(db.Model):
    __tablename__ = 'agriculteurs'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    nom=db.Column(db.Text,nullable=False)
    phone=db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password=db.Column(db.String(255),nullable=False)
    created_at=db.Column(db.Date,default=datetime.utcnow)

    def get_password(self,password):
        return bcrypt.check_password_hash(self.password,password)
"""
class Geometry(UserDefinedType):
    def get_col_spec(self):
        # On définit le type brut pour MySQL
        return "GEOMETRY" 

class Parcelle(db.Model):
    __tablename__ = 'parcelles'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('agriculteurs.id'), nullable=False)
    nom=db.Column(db.Text,nullable=False)
    phone=db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password=db.Column(db.String(255),nullable=False)
    created_at=db.Column(db.Date,default=datetime.utcnow)
    culture_type = db.Column(db.String(50), nullable=False)
    geometrie = db.Column(Geometry, nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' ou 'admin'
    #latitude_init = db.Column(db.Float, nullable=False)
    #longitude_init = db.Column(db.Float, nullable=False)
    @property
    def surface_ha(self):
        # On demande à la base de données de faire le calcul ellipsoïdal
        area_m2 = db.session.query(func.ST_Area(self.geometrie)).scalar()
        return area_m2 / 10000 if area_m2 else 0

    def get_password(self,password):
        return bcrypt.check_password_hash(self.password,password)

class Scan(db.Model):
    __tablename__ = 'scans'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parcelle_id = db.Column(db.Integer, db.ForeignKey('parcelles.id'), nullable=False)
    date_analyse = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(255)) # Chemin de la photo analysée
    statut_sante = db.Column(db.String(50)) # SAIN / MALADE / REJETÉ
    diagnostic = db.Column(db.Text)
    facteur_sante = db.Column(db.Float) # Pour tracer la courbe de santé
    protocole_json = db.Column(db.JSON) # Stocke tout le JSON de l'IA pour historique

class Analytics(db.Model):
    __tablename__ = 'analytics'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(50), nullable=False) # 'login', 'scan', 'register'
    parcelle_id = db.Column(db.Integer, db.ForeignKey('parcelles.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.JSON) # Informations supplémentaires (IP, user_agent, etc.)

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parcelle_id = db.Column(db.Integer, db.ForeignKey('parcelles.id'), nullable=False)
    reset_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 

def app_context(app):
    with app.app_context():
        # 1. Création des tables de base
        db.create_all()
        
        # 2. Correction manuelle pour MySQL (Optionnel mais recommandé)
        # On force la colonne à accepter le SRID 4326 si ce n'est pas fait
        try:
            db.session.execute(text("ALTER TABLE parcelles MODIFY geometrie GEOMETRY SRID 4326 NOT NULL;"))
            db.session.commit()
        except Exception as e:
            print("Note: La colonne est déjà configurée ou MySQL refuse l'ALTER.")
