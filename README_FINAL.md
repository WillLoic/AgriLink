# AgriLink - Analyse Agricole IA

Plateforme d'analyse agricole utilisant l'intelligence artificielle pour évaluer la santé des cultures et générer des scores de crédibilité agricole.

## 🚀 Fonctionnalités Principales

### ✅ Implémentées
- **Analyse IA** : Diagnostic automatique avec Google Gemini
- **Gestion parcellaire** : Délimitation GPS des champs
- **Score agricole** : Calcul de crédibilité basé sur l'historique
- **Rapports PDF** : Certificats de crédibilité
- **Authentification JWT** : Connexion sécurisée
- **Mot de passe oublié** : Réinitialisation par email
- **Analytics admin** : Statistiques d'utilisation (réservé aux admins)

### 🔧 Configuration Requise

## 📋 Installation & Configuration

### 1. Variables d'environnement
Créez un fichier `.env` à partir de `.env.example` :

```bash
# Base de données
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:@localhost/agrilink_db

# JWT
SECRET_KEY=votre_cle_secrete_super_longue_et_complexe

# Email (obligatoire pour mot de passe oublié)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre.email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_app
MAIL_DEFAULT_SENDER=noreply@agri-link.com

# Google Gemini AI
GEMINI_API_KEY=votre_cle_api_gemini
```

### 2. Migration de base de données
```bash
# Appliquer les nouvelles tables
python Backend/migrate.py
```

### 3. Définir un administrateur
```bash
# Lister les utilisateurs
python set_admin.py list

# Définir un utilisateur comme admin
python set_admin.py votre.email@exemple.com
```

### 4. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 5. Lancement
```bash
# Terminal 1 - Backend
python Backend/app.py

# Terminal 2 - Frontend
cd Frontend
streamlit run front.py
```

## 🎯 Instructions pour Finaliser le Projet

### ✅ Modifications Appliquées
- ✅ Modèles `Analytics` et `PasswordReset` créés
- ✅ Service de réinitialisation de mot de passe
- ✅ Endpoints API pour mot de passe oublié et analytics
- ✅ Pages frontend pour mot de passe oublié
- ✅ Système de rôles (user/admin)
- ✅ Analytics réservés aux administrateurs
- ✅ Logging automatique des événements

### 🔧 Actions à Faire par Vous

#### 1. Configuration Email (OBLIGATOIRE)
```bash
# Dans votre fichier .env, configurez :
MAIL_USERNAME=votre.email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_application_gmail
```

**Comment obtenir un mot de passe d'application Gmail :**
1. Allez dans votre compte Google > Sécurité
2. Activer la "Vérification en 2 étapes"
3. Générer un "Mot de passe d'application"
4. Utiliser ce mot de passe (pas votre mot de passe normal)

#### 2. Tester les Fonctionnalités
```bash
# 1. Lancer la migration
python Backend/migrate.py

# 2. Créer un compte admin
python set_admin.py votre.email@exemple.com

# 3. Tester le mot de passe oublié
# - Aller sur la page de connexion
# - Cliquer "Mot de passe oublié"
# - Entrer votre email
# - Vérifier votre boîte mail

# 4. Tester les analytics (en tant qu'admin)
# - Se connecter avec un compte admin
# - Vérifier la section "Statistiques Globales" dans le dashboard
```

#### 3. Vérifications Importantes
- [ ] Le backend se lance sans erreur
- [ ] Le frontend se lance avec `streamlit run front.py`
- [ ] L'inscription fonctionne
- [ ] La connexion fonctionne
- [ ] Le mot de passe oublié envoie un email
- [ ] Les analytics s'affichent pour les admins uniquement

### 🚨 Points d'Attention

1. **Email Configuration** : Sans configuration email correcte, le mot de passe oublié ne fonctionnera pas
2. **Rôles Admin** : Seuls les utilisateurs avec `role='admin'` voient les analytics
3. **Migration** : La migration doit être exécutée une seule fois après les modifications
4. **Variables d'environnement** : Le fichier `.env` doit être créé et configuré

## 📊 API Endpoints

### Authentification
- `POST /api/v1/register` - Inscription
- `POST /api/v1/login` - Connexion
- `POST /api/v1/forgot-password` - Demande réinitialisation MDP
- `POST /api/v1/reset-password` - Réinitialisation MDP

### Utilisateur
- `GET /api/v1/user/profile` - Profil utilisateur

### Analyses & Dashboard
- `POST /api/v1/scan` - Analyse IA d'une photo
- `GET /api/v1/dashboard/stats` - Statistiques utilisateur
- `GET /api/v1/dashboard/certificat` - Génération PDF
- `GET /api/v1/analytics` - Statistiques globales (admin uniquement)

## 🎨 Pages Frontend

- `front.py` - Page d'accueil
- `pages/auth.py` - Connexion/Inscription + lien MDP oublié
- `pages/dashboard.py` - Dashboard + analytics (admin)
- `pages/scan.py` - Analyse de photos
- `pages/historique.py` - Historique des analyses
- `pages/forgot_password.py` - Mot de passe oublié
- `pages/reset_password.py` - Réinitialisation MDP

## 🔒 Sécurité

- JWT pour l'authentification
- Hashage bcrypt des mots de passe
- Tokens de réinitialisation à expiration (1h)
- Rôles utilisateurs (user/admin)
- Logs d'activité automatiques

---

**🎉 Une fois ces étapes complétées, votre AgriLink sera entièrement fonctionnel avec toutes les fonctionnalités demandées !**