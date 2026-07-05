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
- Routage par rôle (utilisateur / administrateur)
- Dashboard utilisateur avec interface chatbot
- Dashboard administrateur (statistiques et aperçu plateforme)
- Profil utilisateur partagé (consultation, modification, photo, suppression)
- Changement de mot de passe (utilisateur et administrateur)
- Complétion obligatoire du profil (date de naissance + région) — utilisateurs uniquement
- Notifications toast pour les actions profil
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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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

## Accès depuis un téléphone

En développement, le frontend et le backend écoutent sur toutes les interfaces réseau (`0.0.0.0`). Vous pouvez tester l'application depuis un téléphone connecté au même Wi-Fi.

### 1. Connaître l'adresse IP du PC

**macOS :**
```bash
ipconfig getifaddr en0
```

**Linux :**
```bash
hostname -I | awk '{print $1}'
```

**Windows (PowerShell) :**
```powershell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi").IPAddress
```

Remplacez `192.168.x.x` ci-dessous par l'adresse affichée.

### 2. Lancer le backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Lancer le frontend

```bash
cd frontend
npm run dev
```

Vite affiche l'URL réseau dans le terminal (ex. `http://192.168.x.x:5173`).

### 4. Ouvrir sur le téléphone

Dans le navigateur du téléphone, ouvrez :

```
http://192.168.x.x:5173
```

L'API est contactée automatiquement sur `http://192.168.x.x:8000` (même hôte que le frontend). Aucune modification de `.env` n'est nécessaire tant que le backend tourne sur le port 8000.

> **PC :** l'accès via `http://localhost:5173` continue de fonctionner normalement.

## Navigation

```
Home → Register → Login → Dashboard (utilisateur ou administrateur)
```

### Pages publiques

- **Home** (`/`) — page visiteur
- **Register** (`/register`) — création de compte
- **Login** (`/login`) — connexion

### Dashboard utilisateur (rôle `utilisateur`)

- **Dashboard** (`/dashboard`) — espace chatbot (protégé)
- **Profil** (`/dashboard/profil`) — gestion du profil (protégé)
- **Mot de passe** (`/dashboard/changer-mot-de-passe`) — changement de mot de passe (protégé)

### Dashboard administrateur (rôle `administrateur`)

- **Tableau de bord** (`/admin`) — statistiques et aperçu plateforme (protégé)
- **Profil** (`/admin/profil`) — gestion du profil admin (protégé)
- **Mot de passe** (`/admin/changer-mot-de-passe`) — changement de mot de passe (protégé)

> Après connexion, l'utilisateur est redirigé automatiquement vers `/dashboard` ou `/admin` selon son rôle.

## Documentation détaillée

- [Frontend README](frontend/README.md)
- [Backend README](backend/README.md)

## Licence

Projet éducatif — AidFinder.
