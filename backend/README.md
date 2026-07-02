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
```

## Initialisation de la base de données

```bash
python -m app.create_tables
```

## Lancement

```bash
uvicorn app.main:app --reload --port 8000
```

L'API est accessible sur [http://localhost:8000](http://localhost:8000).

Documentation interactive : [http://localhost:8000/docs](http://localhost:8000/docs)

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
| PATCH   | `/users/photo`     | Upload photo de profil             | Oui  |

## Statuts de compte (`statut_compte`)

| Valeur                  | Description                                      |
|-------------------------|--------------------------------------------------|
| `actif`                 | Compte fonctionnel                               |
| `desactive_utilisateur` | Pause volontaire — réactivation auto à la connexion |
| `suspendu_admin`        | Suspension admin — connexion refusée (403)       |

> Compatibilité : l'ancienne valeur `desactive` est traitée comme `desactive_utilisateur`.

## CORS

Le middleware CORS autorise les requêtes depuis `http://localhost:5173` (frontend Vite).
