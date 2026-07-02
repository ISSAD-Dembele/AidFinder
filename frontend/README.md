# AidFinder — Frontend

Interface utilisateur de la plateforme AidFinder, développée avec React et Vite.

## Stack technique

- **React 19** (JavaScript)
- **Vite 8** — bundler et serveur de développement
- **Tailwind CSS v4** — styles utilitaires
- **ShadCN UI** (Radix) — composants UI
- **React Router v7** — navigation
- **Axios** — requêtes HTTP vers l'API FastAPI

## Prérequis

- Node.js 18+
- npm

## Installation

```bash
cd frontend
npm install
cp .env.example .env
```

## Variables d'environnement

| Variable        | Description              | Valeur par défaut        |
|-----------------|--------------------------|--------------------------|
| `VITE_API_URL`  | URL de l'API FastAPI     | `http://localhost:8000`  |

## Lancement

```bash
npm run dev
```

L'application est accessible sur [http://localhost:5173](http://localhost:5173).

## Scripts disponibles

| Commande         | Description                    |
|------------------|--------------------------------|
| `npm run dev`    | Serveur de développement       |
| `npm run build`  | Build de production            |
| `npm run preview`| Prévisualisation du build      |
| `npm run lint`   | Analyse ESLint                 |

## Architecture des dossiers

```
frontend/
├── components/
│   └── ui/              # Composants ShadCN (Button, Input, Card…)
├── lib/
│   └── utils.js         # Utilitaires (cn, etc.)
├── public/              # Assets statiques
├── src/
│   ├── assets/          # Images et illustrations
│   ├── components/      # Composants métier (Navbar, Sidebar, Profil…)
│   ├── constants/       # Options de formulaire (régions, statuts…)
│   ├── contexts/        # Contextes React (AuthContext, ProfileContext)
│   ├── layouts/         # Layouts (Public, Dashboard)
│   ├── pages/           # Pages (Home, Login, Register, Dashboard, Profil…)
│   ├── services/        # Appels API (api.js, auth.js, user.js)
│   └── utils/           # Utilitaires frontend
├── index.html
├── vite.config.js
└── package.json
```

## Pages développées

| Route                            | Page                    | Accès        |
|----------------------------------|-------------------------|--------------|
| `/`                              | Home                    | Public       |
| `/register`                      | Inscription             | Public       |
| `/login`                         | Connexion               | Public       |
| `/dashboard`                     | Dashboard (chat)        | Authentifié  |
| `/dashboard/profil`              | Profil utilisateur      | Authentifié  |
| `/dashboard/changer-mot-de-passe`| Changement mot de passe | Authentifié  |

## Complétion du profil

À la première connexion, si la **date de naissance** ou la **région** sont absentes, une fenêtre modale obligatoire s'affiche avant l'accès au Dashboard. Les champs facultatifs (niveau d'étude, statut socioprofessionnel, handicap) peuvent être complétés plus tard depuis la page Profil.

## Authentification

- Le JWT est stocké dans `localStorage` après connexion
- Les routes privées sont protégées via `ProtectedRoute`
- La désactivation du compte appelle `PATCH /auth/deactivate` puis redirige vers Home

## Connexion au backend

Les services dans `src/services/` communiquent avec les routes FastAPI :

**Authentification (`auth.js`)**
- `POST /auth/register` — inscription
- `POST /auth/login` — connexion (retourne un JWT)
- `PATCH /auth/deactivate` — désactivation volontaire du compte

**Profil utilisateur (`user.js`)**
- `GET /users/me` — consultation du profil
- `PATCH /users/me` — modification du profil
- `PATCH /users/change-password` — changement du mot de passe
- `PATCH /users/photo` — upload de la photo de profil
