# AidFinder

AidFinder est une plateforme web intelligente permettant de rechercher des aides financières selon le profil utilisateur, grâce à un chatbot IA.

## Présentation

L'application aide les utilisateurs à identifier les aides financières auxquelles ils ont droit, via une interface moderne et un assistant conversationnel.

## Stack technique

### Frontend
- React 19 + Vite 8
- Tailwind CSS v4
- ShadCN UI (Radix)
- React Router v7
- Axios

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT + OAuth2
- Pydantic

### IA (à venir)
- API LLM pour le chatbot

## Fonctionnalités

- Authentification (inscription, connexion, désactivation volontaire)
- Dashboard utilisateur avec interface chatbot
- Profil utilisateur (consultation, modification, photo)
- Changement de mot de passe
- Complétion obligatoire du profil (date de naissance + région)
- Recherche d'aides (à venir)
- Historique (à venir)
- Export PDF (à venir)
- Design responsive (mobile first)

## Structure du projet

```
AidFinder/
├── backend/          # API FastAPI + PostgreSQL
├── frontend/         # Interface React + Vite
├── docs/
│   ├── maquettes/    # Maquettes UI
│   ├── uml/          # Diagrammes UML
│   └── achitecture/  # Diagrammes d'architecture
└── README.md
```

## Installation après clonage

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créer le fichier `.env` (voir [backend/README.md](backend/README.md)) puis :

```bash
python -m app.create_tables
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3. Accès

| Service   | URL                              |
|-----------|----------------------------------|
| Frontend  | http://localhost:5173            |
| Backend   | http://localhost:8000            |
| API Docs  | http://localhost:8000/docs       |

## Navigation

```
Home → Register → Login → Dashboard
```

- **Home** (`/`) — page visiteur
- **Register** (`/register`) — création de compte
- **Login** (`/login`) — connexion
- **Dashboard** (`/dashboard`) — espace utilisateur (protégé)
- **Profil** (`/dashboard/profil`) — gestion du profil (protégé)
- **Mot de passe** (`/dashboard/changer-mot-de-passe`) — changement de mot de passe (protégé)

## Documentation détaillée

- [Frontend README](frontend/README.md)
- [Backend README](backend/README.md)

## Licence

Projet éducatif — AidFinder.
