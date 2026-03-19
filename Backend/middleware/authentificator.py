from flask import request,make_response
import jwt
from app import app
from models.config import Parcelle
from functools import wraps

#mise en place du decorateur
def authentificate_required(fonction):
    @wraps(fonction)
    def wrapper(*args,**kwargs):
        auth_headers=request.headers.get('Authorization')
        if not auth_headers: 
            return make_response({'msg':'Token manquant'},401)
        else:
            try:
                token=auth_headers.split(" ")[1]#on recupere le token apres le bearer
                token_decode=jwt.decode(token,app.config['SECRET_KEY'],algorithms='HS256')
            except IndexError:
                return make_response({'msg': 'Format du token invalide'}, 401)
            except jwt.ExpiredSignatureError:
                return make_response({'msg': 'Token expire'}, 401)
            except jwt.InvalidTokenError:
                return make_response({'msg': 'Token invalide'}, 401)
            agriculteur=Parcelle.query.filter_by(id=token_decode.get('id')).first()
            if agriculteur:
                return fonction(current_user=agriculteur,*args,**kwargs)
            else:
                return make_response({'msg':'Utilisateur non trouve'}, 401)
    return wrapper
