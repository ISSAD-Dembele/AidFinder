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
│   ├── contexts/        # Contextes React (AuthContext, ProfileContext, ToastContext)
│   ├── layouts/         # Layouts (Public, Dashboard, AdminDashboard)
│   ├── pages/           # Pages (Home, Login, Register, Dashboard, Profil…)
│   ├── services/        # Appels API (api.js, auth.js, user.js)
│   └── utils/           # Utilitaires frontend
├── index.html
├── vite.config.js
└── package.json
```

## Pages développées

| Route                             | Page                    | Accès                    |
|-----------------------------------|-------------------------|--------------------------|
| `/`                               | Home                    | Public                   |
| `/register`                       | Inscription             | Public                   |
| `/login`                          | Connexion               | Public                   |
| `/dashboard`                      | Dashboard (chat)        | Authentifié (utilisateur)|
| `/dashboard/profil`               | Profil utilisateur      | Authentifié (utilisateur)|
| `/dashboard/changer-mot-de-passe` | Changement mot de passe | Authentifié (utilisateur)|
| `/admin`                          | Dashboard administrateur| Authentifié (admin)      |
| `/admin/profil`                   | Profil administrateur   | Authentifié (admin)      |
| `/admin/changer-mot-de-passe`     | Changement mot de passe | Authentifié (admin)      |

## Routage par rôle

- Le rôle est récupéré via `GET /users/me` après connexion et stocké dans `AuthContext`
- `ProtectedRoute` vérifie l'authentification et le rôle (`utilisateur` ou `administrateur`)
- Un utilisateur connecté est redirigé vers son dashboard s'il tente d'accéder à une route d'un autre rôle
- Les pages **Profil** et **Changement de mot de passe** sont partagées entre les deux rôles

## Dashboard administrateur

Interface conforme à la maquette `docs/maquettes/Dashbord_admin.png` :

- Cartes statistiques (données mockées en attendant l'API admin)
- Liste des aides récentes
- Graphique d'activité des 7 derniers jours
- Sidebar avec navigation (Utilisateurs, Aides, Statistiques — à venir)

## Complétion du profil

À la première connexion, si la **date de naissance** ou la **région** sont absentes, une fenêtre modale obligatoire s'affiche avant l'accès au Dashboard utilisateur. Cette contrainte ne s'applique pas aux administrateurs. Les champs facultatifs (niveau d'étude, statut socioprofessionnel, handicap) peuvent être complétés plus tard depuis la page Profil.

## Notifications toast

Le `ToastProvider` affiche des confirmations légères (ex. : photo de profil mise à jour ou supprimée).

## Authentification

- Le JWT est stocké dans `localStorage` après connexion
- Les routes privées sont protégées via `ProtectedRoute` (avec contrôle de rôle)
- La désactivation du compte appelle `PATCH /auth/deactivate` puis redirige vers Home

## Connexion au backend

Les services dans `src/services/` communiquent avec les routes FastAPI :

**Authentification (`auth.js`)**
- `POST /auth/register` — inscription
- `POST /auth/login` — connexion (retourne un JWT)
- `PATCH /auth/deactivate` — désactivation volontaire du compte

**Profil utilisateur (`user.js`)**
- `GET /users/me` — consultation du profil (inclut le rôle)
- `PATCH /users/me` — modification du profil (photo_profil: null pour supprimer)
- `PATCH /users/change-password` — changement du mot de passe
- `PATCH /users/photo` — upload de la photo de profil
