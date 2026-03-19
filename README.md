# AgriLink - Analyse Agricole IA

Plateforme d'analyse agricole utilisant l'intelligence artificielle pour évaluer la santé des cultures et générer des scores de crédibilité agricole.

---

## ✅ Fonctionnalités clés

- **Analyse IA (Gemini 2.5 Flash)** : Diagnostic agronomique à partir d'une photo
- **Gestion de parcelles** : Enregistrement des coordonnées GPS et type de culture
- **Score agricole** : Calcul de crédibilité basé sur l'historique
- **Rapport PDF** : Génération de certificats téléchargeables
- **Authentication JWT** : Connexion sécurisée avec tokens
- **Mot de passe oublié** : Réinitialisation par email (token expirant)
- **Quotas de scans** : Limitation à 10 scans/jour + blocage après 3 scans consécutifs
- **Analytics admin** : Statistiques et historique (accessible aux admins)
- **Panel d'administration** : Promotion/rétrogradation des utilisateurs

---

## 🧩 Structure du projet

```
AGRILINK/
├── Backend/          # API Flask + logique métier
├── Frontend/         # Application Streamlit (UI)
├── requirements.txt  # Dépendances Python
└── README.md         # Documentation
```

---

## ⚙️ Installation & Configuration (Local)

### 1) Prérequis

- Python 3.8+
- MySQL 8+ (ou compatible)
- Compte Google (pour Gemini API)
- Compte Gmail + mot de passe d'application (pour l'email)

### 2) Variables d'environnement
Copiez `.env.example` vers `.env` et remplissez :

```bash
cp .env.example .env
```

Éditez `.env` avec vos valeurs :

```env
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:@localhost/agrilink_db
SECRET_KEY=votre_cle_secrete_super_longue

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=votre.email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_application_gmail
MAIL_DEFAULT_SENDER=noreply@agri-link.com

GEMINI_API_KEY=votre_cle_api_gemini
```

> ✅ **Important** : pour Gmail, utilisez un mot de passe d'application (2FA requis).

### 3) Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4) Initialiser la base de données

```bash
python migrate.py
```

### 5) Créer un administrateur

```bash
python set_admin.py votre.email@exemple.com
```

### 6) Lancer l'application

```bash
# Backend
cd Backend
python app.py

# Frontend
cd Frontend
streamlit run app.py
```

---

## 🧠 Quotas de scans (limitation API Gemini)

Pour éviter d'épuiser le quota gratuit, l'application limite :

- 🔢 **10 scans par jour**
- 🧱 **Blocage 10 minutes** après **3 scans consécutifs**

### Ce qui est affiché à l'utilisateur
- Nombre de scans effectués aujourd'hui
- Nombre restant
- Blocage et temps restant si le quota est atteint

---

## 🗂️ Endpoints principaux

### Authentification
- `POST /api/v1/register` - Inscription
- `POST /api/v1/login` - Connexion (JWT)
- `POST /api/v1/forgot-password` - Demande de réinitialisation
- `POST /api/v1/reset-password` - Réinitialisation (token)

### Scans & Dashboard
- `POST /api/v1/scan` - Lancer une analyse IA
- `GET /api/v1/scan/quota` - Voir quotas journaliers
- `GET /api/v1/dashboard/stats` - Statistiques utilisateur
- `GET /api/v1/dashboard/certificat` - PDF de score

### Administration
- `GET /api/v1/analytics` - Statistiques globales (admin)
- `GET /api/v1/user/profile` - Profil connecté

---

## 🚀 En production (conseils)

### 1) Serveur web (Nginx)

Configurez un reverse proxy pour rediriger :
- `/api` vers le backend Flask
- `/` vers le frontend Streamlit

### 2) Service systemd

```ini
[Unit]
Description=AgriLink Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/AGRILINK/Backend
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3) Environnement de production
- Utiliser des variables d'environnement sécurisées
- Ne pas stocker les clés d’API dans le repo

---

## 🧪 Tests

```bash
pytest Backend/tests/
```

---

## 🚑 Debug / FAQ rapide

### Mot de passe oublié ne fonctionne pas
- Vérifiez que les variables email sont correctes
- Assurez-vous que votre SMTP accepte l’envoi (Gmail -> mot de passe d’app)

### Quota Gemini atteint
- Limité à **10 scans/jour** et **3 scans d’affilée**
- Attendez **10 minutes** ou **le lendemain**

### Erreur de connexion à la base MySQL
- Vérifiez que le serveur MySQL tourne
- Vérifiez `SQLALCHEMY_DATABASE_URI` dans `.env`

---

**Bonne continuation avec AgriLink ! 🌱**

### 4. Lancement
```bash
# Backend
python Backend/app.py

# Frontend (dans un autre terminal)
cd Frontend
streamlit run front.py
```

## 📋 API Endpoints

### Authentification
- `POST /api/v1/register` - Inscription
- `POST /api/v1/login` - Connexion
- `POST /api/v1/forgot-password` - Demande réinitialisation MDP
- `POST /api/v1/reset-password` - Réinitialisation MDP

### Analyses & Dashboard
- `POST /api/v1/scan` - Analyse IA d'une photo
- `GET /api/v1/dashboard/stats` - Statistiques utilisateur
- `GET /api/v1/dashboard/certificat` - Génération PDF
- `GET /api/v1/analytics` - Statistiques globales

## 🎨 Pages Frontend

- `front.py` - Page d'accueil
- `pages/auth.py` - Connexion/Inscription
- `pages/dashboard.py` - Tableau de bord + Analytics
- `pages/scan.py` - Analyse de photos
- `pages/historique.py` - Historique des analyses
- `pages/forgot_password.py` - Mot de passe oublié
- `pages/reset_password.py` - Réinitialisation MDP

## 🔧 Technologies Utilisées

- **Backend** : Flask, SQLAlchemy, JWT, Flask-Mail
- **Frontend** : Streamlit, CSS personnalisé
- **IA** : Google Gemini 1.5 Pro
- **Base de données** : MySQL avec géométrie spatiale
- **Email** : SMTP avec templates HTML

## 📊 Schéma Base de Données

### Tables existantes
- `parcelles` - Informations agriculteurs
- `scans` - Analyses IA effectuées

### Nouvelles tables (v2.0)
- `analytics` - Suivi des événements (login, scan, register)
- `password_resets` - Tokens de réinitialisation MDP

## 🔒 Sécurité

- JWT pour l'authentification
- Hashage bcrypt des mots de passe
- Tokens de réinitialisation à expiration
- Validation des emails et mots de passe
- Logs d'activité pour analytics

## 🌱 Fonctionnalités Clés

1. **Analyse IA** : Diagnostic automatique de la santé des plantes
2. **Score agricole** : Calcul de crédibilité basé sur l'historique
3. **Gestion parcellaire** : Délimitation GPS des champs
4. **Rapports PDF** : Certificats de crédibilité
5. **Réinitialisation MDP** : Récupération de compte sécurisée
6. **Analytics temps réel** : Statistiques d'utilisation

---

**Développé avec ❤️ pour la révolution agricole**