# AidFinder — Backend

API REST développée avec FastAPI pour la plateforme AidFinder.

## Stack technique

- **FastAPI** — framework web
- **PostgreSQL** — base de données
- **SQLAlchemy** — ORM
- **Pydantic** — validation des données
- **JWT** — authentification (python-jose)
- **OAuth2** — schéma de sécurité (Bearer token)
- **Passlib + bcrypt** — hashage des mots de passe

## Prérequis

- Python 3.11+
- PostgreSQL

## Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Variables d'environnement

Créer un fichier `.env` à la racine du dossier `backend/` :

```env
DATABASE_URL=postgresql://user:password@localhost:5432/aidfinder
SECRET_KEY=votre_cle_secrete
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Qwen / DashScope compatible OpenAI
QWEN_API_KEY=votre_cle_api_qwen
QWEN_API_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions
QWEN_MODEL=qwen-plus
QWEN_MAX_TOKENS=700
QWEN_TEMPERATURE=0.2
QWEN_TIMEOUT_SECONDS=30

# Serveur (développement)
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Voir `.env.example` pour la liste complète des variables.

## Initialisation de la base de données

```bash
python -m app.create_tables
```

## Lancement

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur [http://localhost:8000](http://localhost:8000) (PC) et sur `http://<IP-locale>:8000` (réseau local).

Documentation interactive : [http://localhost:8000/docs](http://localhost:8000/docs)

## Accès depuis un téléphone

Le serveur doit écouter sur `0.0.0.0` (valeur par défaut de `HOST` dans `.env`) :

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le frontend sur le téléphone appellera l'API à `http://<IP-du-PC>:8000`. Vérifier que le pare-feu autorise les connexions entrantes sur les ports 5173 et 8000.

## Architecture des dossiers

```
backend/
├── app/
│   ├── core/           # Configuration et sécurité (JWT, hash)
│   ├── database/       # Connexion PostgreSQL et sessions
│   ├── models/         # Modèles SQLAlchemy
│   ├── routes/         # Routes FastAPI
│   ├── schemas/        # Schémas Pydantic
│   ├── services/       # Logique métier
│   ├── create_tables.py
│   └── main.py         # Point d'entrée FastAPI
└── requirements.txt
```

## Routes disponibles

| Méthode | Route              | Description              | Auth |
|---------|--------------------|--------------------------|------|
| POST    | `/auth/register`   | Inscription utilisateur  | Non  |
| POST    | `/auth/login`      | Connexion (retourne JWT) | Non  |
| PATCH   | `/auth/deactivate` | Désactivation volontaire du compte | Oui  |
| GET     | `/users/me`        | Consultation du profil             | Oui  |
| PATCH   | `/users/me`        | Modification du profil             | Oui  |
| PATCH   | `/users/change-password` | Changement du mot de passe   | Oui  |
| PATCH   | `/users/photo`     | Upload photo de profil (jpg, jpeg, png, webp, heic) | Oui  |
| POST    | `/dashboard/chat`  | Message chatbot connecté au profil, recommandations et mémoire | Oui |

## Statuts de compte (`statut_compte`)

| Valeur                  | Description                                      |
|-------------------------|--------------------------------------------------|
| `actif`                 | Compte fonctionnel                               |
| `desactive_utilisateur` | Pause volontaire — réactivation auto à la connexion |
| `suspendu_admin`        | Suspension admin — connexion refusée (403)       |

> Compatibilité : l'ancienne valeur `desactive` est traitée comme `desactive_utilisateur`.

## Rôles utilisateur

| Rôle              | Dashboard frontend | Description                          |
|-------------------|--------------------|--------------------------------------|
| `utilisateur`     | `/dashboard`       | Compte standard — recherche d'aides  |
| `administrateur`  | `/admin`           | Gestion de la plateforme             |

> Les comptes administrateurs sont créés directement en base de données (table `utilisateurs` avec `role = 'administrateur'` et entrée associée dans `administrateurs`).

## Routes admin (à venir)

Les endpoints de gestion (utilisateurs, aides, statistiques) seront ajoutés dans une prochaine itération.

## CORS

Le middleware CORS autorise :

- `http://localhost:5173` et `http://127.0.0.1:5173` (PC)
- Les origines du réseau local privé sur le port 5173 (ex. `http://192.168.x.x:5173`) via une regex configurable

Variables dans `.env` :

| Variable             | Description                                      |
|----------------------|--------------------------------------------------|
| `CORS_ORIGINS`       | Origines explicites (séparées par des virgules)  |
| `CORS_ORIGIN_REGEX`  | Regex pour les IP privées ; laisser vide pour désactiver |
