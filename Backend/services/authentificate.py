from flask import Flask, request, jsonify
from models.config import Parcelle,db
from sqlalchemy import text
import json
import jwt
from datetime import datetime, timedelta
from app import app
from flask_bcrypt import Bcrypt
bcrypt=Bcrypt()


class AgriculteurModels():
    """
    def register(self):
        try:
            nom = request.form['nom']
            phone = request.form['phone']
            email = request.form['email']
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            #agriculteurs = Parcelle(nom=nom,phone=phone,email=email,password=password)
            culture_type = request.form.get('culture_type')
            coords_json = request.form.get('coords') 

            # 1. Conversion de la chaîne JSON en liste Python
            points = json.loads(coords_json) # Ex: [[lat, lon], [lat, lon], ...]

            if len(points) < 3:
                return jsonify({"error": "Un champ doit avoir au moins 3 points"}), 400

            # 2. Rigueur : Fermer le polygone
            # En géométrie, le premier et le dernier point doivent être identiques
            if points[0] != points[-1]:
                    points.append(points[0])

            # 3. Formatage pour MySQL (POLYGON((lat lon, lat lon, ...)))
            # Note : On utilise des espaces entre lat/lon et des virgules entre les points
            wkt_points = ", ".join([f"{p[0]} {p[1]}" for p in points])
            wkt_polygon = f"POLYGON(({wkt_points}))"
            # 4. Insertion en base de données avec SQLAlchemy text()
            sql = text(
                    INSERT INTO parcelles (nom, phone, email, password, created_at, culture_type, geometrie) 
                    VALUES (:nom, :phone, :email, :password, :created_at, :culture_type, ST_GeomFromText(:poly, 4326))
                )
                
            result=db.session.execute(sql, {"nom":nom, "phone":phone, "email":email, "password":password, "created_at":datetime.utcnow(), "culture_type":culture_type,"poly":wkt_polygon})

            db.session.commit()

            # Logger l'événement d'inscription
            from services.password_reset import AnalyticsService
            analytics = AnalyticsService()
            # Récupérer l'ID de la parcelle créée
            parcelle_id = result.lastrowid
            analytics.log_event('register', parcelle_id, {
                'email': email,
                'culture_type': culture_type,
                'ip_address': request.remote_addr
            })

            return jsonify({'msg':'Inscription reussi'}),200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500"""

    def register(self):
        try:
            nom = request.form['nom']
            phone = request.form['phone']
            email = request.form['email']
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            culture_type = request.form.get('culture_type')
            
            new_parcelle = Parcelle(
            nom=nom,
            phone=phone,
            email=email,
            password=password,
            created_at=datetime.utcnow(),
            culture_type=culture_type,
            role='user',
            geometrie=None # SQLAlchemy transformera ça en NULL pour Postgres ou MySQL
            )

            db.session.add(new_parcelle)
            db.session.commit() # L'ID est généré ici
            
            # 2. Rigueur : Récupérer l'ID de manière universelle
            # SQLAlchemy rafraîchit l'objet automatiquement après le commit
            parcelle_id = new_parcelle.id 

            # Logger l'événement
            from services.password_reset import AnalyticsService
            analytics = AnalyticsService()
            analytics.log_event('register', parcelle_id, {
                'email': email,
                'culture_type': culture_type,
                'ip_address': request.remote_addr
            })

            return jsonify({'msg':'Inscription réussie'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur Inscription: {str(e)}")
            return jsonify({'error': str(e)}), 500


    def login(self):
        password = request.form['password']
        phone = request.form['phone']
        agriculteur = Parcelle.query.filter_by(phone=phone).first()
        if agriculteur:
            if agriculteur.get_password(password):
            #if password==agent.password:
                payload={'id':agriculteur.id,'exp':datetime.utcnow()+timedelta(days=1)}
                token=jwt.encode(payload,app.config['SECRET_KEY'],algorithm='HS256')

                # Logger l'événement de connexion
                from services.password_reset import AnalyticsService
                analytics = AnalyticsService()
                analytics.log_event('login', agriculteur.id, {
                    'phone': phone,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent')
                })

                return jsonify({"token": token}), 200
            else:
                return jsonify({"message": "Mot de passe incorrect"}), 401
        else:
            return jsonify({"message": "Utilisateur non trouvé"}), 401
