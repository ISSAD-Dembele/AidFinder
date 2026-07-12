# AidFinder — Frontend

Interface utilisateur moderne de la plateforme AidFinder, développée avec **React 19** et **Vite 8**. Le frontend offre une expérience conversationnelle temps réel avec streaming IA, un dashboard personnalisé, et une interface d'administration complète.

---

## 📋 Présentation

### Objectif
Offrir une expérience utilisateur fluide et intuitive pour permettre aux citoyens marocains de découvrir les aides sociales auxquelles ils sont éligibles, via un chatbot intelligent et un tableau de bord personnalisé.

### Problématique
Les citoyens marocains ont difficilement accès à l'information sur les aides sociales disponibles. Les interfaces administratives sont complexes et peu engageantes. AidFinder résout ce problème avec une interface conversationnelle moderne et mobile-first.

### Solution proposée
Une application web **responsive** qui permet de :
- Discuter avec un **chatbot IA** pour découvrir des aides personnalisées
- Visualiser un **dashboard** avec ses aides recommandées et son historique
- Gérer son **profil** et ses informations personnelles
- Permettre aux **administrateurs** de gérer la plateforme (utilisateurs, aides, scraping)

---

## ✅ Fonctionnalités

### ✅ Terminées
- Page d'accueil publique avec présentation du projet
- Inscription et connexion utilisateur
- Routage par rôle (utilisateur / administrateur)
- Dashboard utilisateur avec interface chatbot temps réel
- Chatbot IA avec **streaming SSE** (affichage progressif des réponses)
- Typing indicator pendant la génération de la réponse
- Suggestions dynamiques après chaque message
- Profil utilisateur (consultation, modification)
- Upload et suppression de photo de profil
- Changement de mot de passe
- Complétion obligatoire du profil (date de naissance + région) à la première connexion
- Historique des conversations chatbot
- Reprise d'une conversation existante
- Aides recommandées personnalisées (page dédiée)
- Consultation des aides récentes
- Dashboard administrateur complet (statistiques, utilisateurs, aides, sources, logs)
- CRUD des aides (admin)
- Gestion des utilisateurs (admin)
- Activation/désactivation des aides (admin)
- Relance manuelle du scraping (admin)
- Notifications toast pour les actions utilisateur
- Navigation responsive (mobile + desktop)

### 🚧 En cours
- Page dédiée aux détails d'une aide
- Filtres avancés pour la recherche d'aides
- Amélioration de l'accessibilité (a11y)

### 📅 Prévues
- Export PDF des aides
- Notifications en temps réel
- Dashboard avec graphiques (Recharts)
- Support multilingue (français / arabe)
- Tests E2E (Playwright / Cypress)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React 19 App                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Pages    │  │  Layouts │  │   Components     │  │
│  │  (Routes) │→│ (Shell)  │→│  (UI + Métier)    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│       │              │              │               │
│       ▼              ▼              ▼               │
│  ┌──────────────────────────────────────────────┐   │
│  │     Contexts (Auth, Profile, Toast)          │   │
│  └──────────────────────────────────────────────┘   │
│       │                                             │
│       ▼                                             │
│  ┌──────────────────────────────────────────────┐   │
│  │     Services (Axios → API FastAPI)            │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Backend FastAPI   │
              │   (backend/README)  │
              └─────────────────────┘
```

### Frontend
Application React monopage (SPA) avec Vite comme bundler. Utilise **Tailwind CSS v4** pour le styling, **ShadCN UI** pour les composants, et **React Router v7** pour la navigation.

### Backend
API REST FastAPI documentée dans [backend/README.md](../backend/README.md).

### Streaming
Le chatbot utilise **Server-Sent Events (SSE)** pour diffuser les réponses du LLM token par token. Le hook `useStreamingChat` gère le cycle de vie : état "thinking" → streaming → terminé.

---

## 🛠️ Stack technique

| Technologie | Rôle |
|-------------|------|
| **React 19** | Framework UI |
| **Vite 8** | Bundler et serveur de développement |
| **Tailwind CSS v4** | Framework CSS utilitaire |
| **ShadCN UI (Radix)** | Composants UI accessibles |
| **React Router v7** | Navigation et routage |
| **Axios** | Client HTTP pour l'API |
| **Framer Motion** | Animations |
| **Lucide React** | Icônes SVG |
| **class-variance-authority** | Gestion des variants CSS |
| **tailwind-merge** | Fusion de classes Tailwind |
| **ESLint** | Linting |
| **@fontsource/geist** | Police typographique Geist |

---

## 📁 Structure du projet

```
frontend/
├── components/
│   └── ui/                    # Composants ShadCN (Button, Input, Card, Dialog, Skeleton, Label)
├── lib/
│   └── utils.js               # Utilitaire cn() pour fusionner les classes Tailwind
├── public/
│   ├── favicon.svg            # Favicon
│   └── icons.svg              # Icônes SVG
├── src/
│   ├── assets/
│   │   ├── images/            # Images diverses
│   │   ├── hero.png           # Image hero de la page d'accueil
│   │   ├── react.svg          # Logo React
│   │   └── vite.svg           # Logo Vite
│   ├── components/
│   │   ├── Logo.jsx           # Composant Logo
│   │   ├── Navbar.jsx         # Barre de navigation
│   │   ├── ProtectedRoute.jsx # Garde de route (auth + rôle)
│   │   ├── admin/             # Composants admin
│   │   ├── dashboard/         # Composants dashboard utilisateur
│   │   ├── home/              # Composants page d'accueil
│   │   └── profile/           # Composants profil
│   ├── config/
│   │   └── env.js             # Configuration de l'URL API (auto-détection hôte)
│   ├── constants/
│   │   └── profileOptions.js  # Options pour les formulaires profil
│   ├── contexts/
│   │   ├── AuthContext.jsx    # Contexte d'authentification
│   │   ├── ProfileContext.jsx # Contexte de profil
│   │   └── ToastContext.jsx   # Contexte de notifications toast
│   ├── hooks/
│   │   ├── useAdminAides.js        # Hook admin — gestion des aides
│   │   ├── useAdminDashboard.js    # Hook admin — dashboard stats
│   │   ├── useAdminLogs.js         # Hook admin — logs scraping
│   │   ├── useAdminSources.js      # Hook admin — sources scraping
│   │   ├── useAdminStats.js        # Hook admin — statistiques
│   │   ├── useAdminUsers.js        # Hook admin — gestion utilisateurs
│   │   ├── useDashboard.js         # Hook dashboard utilisateur
│   │   ├── useHistory.js           # Hook historique conversations
│   │   ├── useRecentAids.js        # Hook aides récentes
│   │   ├── useRecommendations.js   # Hook recommandations
│   │   └── useStreamingChat.js     # Hook streaming SSE chatbot
│   ├── layouts/
│   │   ├── AdminDashboardLayout.jsx # Layout dashboard admin
│   │   ├── DashboardLayout.jsx      # Layout dashboard utilisateur
│   │   └── PublicLayout.jsx         # Layout pages publiques
│   ├── pages/
│   │   ├── admin/
│   │   │   ├── AdminAides.jsx       # Gestion des aides (admin)
│   │   │   ├── AdminSources.jsx     # Gestion des sources (admin)
│   │   │   ├── AdminStats.jsx       # Statistiques (admin)
│   │   │   └── AdminUsers.jsx       # Gestion des utilisateurs (admin)
│   │   ├── AdminDashboard.jsx       # Dashboard administrateur
│   │   ├── AidesRecommandeesPage.jsx # Aides recommandées
│   │   ├── ChangePassword.jsx        # Changement mot de passe
│   │   ├── DashbordUI.jsx            # Dashboard utilisateur (chat)
│   │   ├── DiscussionPage.jsx        # Interface chatbot
│   │   ├── HistoriquePage.jsx        # Historique conversations
│   │   ├── Home.jsx                  # Page d'accueil
│   │   ├── Login.jsx                 # Connexion
│   │   ├── Profile.jsx               # Profil utilisateur
│   │   └── Register.jsx              # Inscription
│   ├── services/
│   │   ├── admin.js              # Service API admin
│   │   ├── api.js                # Instance Axios centralisée (intercepteurs)
│   │   ├── auth.js               # Service API authentification
│   │   ├── dashboardService.js   # Service API dashboard (chat, history)
│   │   ├── home.js               # Service API accueil
│   │   └── user.js               # Service API utilisateur
│   ├── utils/
│   │   ├── aids.js               # Utilitaires aides
│   │   ├── date.js               # Formatage dates
│   │   ├── errors.js             # Gestion d'erreurs
│   │   ├── navigation.js         # Helpers navigation
│   │   └── profile.js            # Utilitaires profil
│   ├── App.css                   # Styles globaux
│   ├── App.jsx                   # Composant racine (routes, providers)
│   ├── index.css                 # Styles Tailwind
│   └── main.jsx                  # Point d'entrée
├── .env.example                  # Exemple de configuration
├── .gitignore
├── components.json               # Configuration ShadCN
├── eslint.config.js              # Configuration ESLint
├── index.html                    # Page HTML
├── jsconfig.json                 # Configuration JS (alias @)
├── package.json                  # Dépendances
├── vite.config.js                # Configuration Vite
└── README.md
```

---

## 🚀 Installation

### Prérequis
- Node.js 18+
- npm

### 1. Cloner le projet

```bash
git clone https://github.com/ISSAD-Dembele/AidFinder.git
cd AidFinder/frontend
```

### 2. Installer les dépendances

```bash
npm install
```

### 3. Configurer l'environnement

```bash
cp .env.example .env
```

### 4. Lancer le serveur de développement

```bash
npm run dev
```

L'application est accessible sur :
- **Local** : http://localhost:5173
- **Réseau local** : l'URL réseau s'affiche dans le terminal (ex: `http://192.168.x.x:5173`)

> **Important** : Le backend FastAPI doit être lancé séparément. Voir [backend/README.md](../backend/README.md).

---

## 🔐 Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `VITE_API_URL` | URL complète de l'API (optionnel) | Déduite automatiquement du navigateur |
| `VITE_API_PORT` | Port du backend si `VITE_API_URL` absent | `8000` |

### Fonctionnement de l'auto-détection

Sans `VITE_API_URL`, le frontend appelle l'API sur le **même hôte** que la page ouverte :
- Sur **PC** (`localhost:5173`) → API appelée sur `localhost:8000`
- Sur **téléphone** (`192.168.x.x:5173`) → API appelée sur `192.168.x.x:8000`

> **Ne pas définir** `VITE_API_URL=http://localhost:8000` si vous testez depuis un téléphone. Sur mobile, `localhost` pointe vers l'appareil, pas vers le PC. Le frontend ignore automatiquement cette valeur lorsqu'il est ouvert depuis une IP réseau.

---

## 📡 Connexion au backend

Les services dans `src/services/` communiquent avec l'API FastAPI via une instance Axios centralisée :

### Authentification (`auth.js`)
| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/auth/register` | Inscription |
| `POST` | `/auth/login` | Connexion (retourne JWT) |
| `PATCH` | `/auth/deactivate` | Désactivation volontaire |

### Profil utilisateur (`user.js`)
| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/users/me` | Consultation du profil (inclut le rôle) |
| `PATCH` | `/users/me` | Modification du profil |
| `PATCH` | `/users/change-password` | Changement mot de passe |
| `PATCH` | `/users/photo` | Upload photo de profil |

### Dashboard & Chat (`dashboardService.js`)
| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/dashboard` | Données du dashboard |
| `GET` | `/dashboard/history` | Historique conversations |
| `GET` | `/dashboard/history/{id}` | Détail d'une conversation |
| `DELETE` | `/dashboard/history/{id}` | Supprimer une conversation |
| `POST` | `/dashboard/chat` | Message chatbot (synchrone) |
| `POST` | `/dashboard/chat/stream` | Message chatbot (streaming SSE) |
| `GET` | `/dashboard/recommendations` | Aides recommandées |
| `GET` | `/dashboard/recent-aids` | Aides consultées récemment |
| `GET` | `/dashboard/stats` | Statistiques utilisateur |

### Accueil (`home.js`)
| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/home/latest-aids` | Dernières aides |
| `GET` | `/api/home/stats` | Statistiques |
| `GET` | `/api/home/categories` | Catégories |
| `GET` | `/api/home/search?q=` | Recherche |

### Administration (`admin.js`)
| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/admin/dashboard` | Dashboard admin |
| `GET` | `/admin/utilisateurs` | Liste utilisateurs |
| `PUT/PATCH/DELETE` | `/admin/utilisateur/{id}` | Gestion utilisateur |
| `GET/POST/PUT` | `/admin/aides` | CRUD aides |
| `GET` | `/admin/sources` | Sources scraping |
| `POST` | `/admin/sources/{id}/scraping` | Relancer scraping |
| `GET` | `/admin/statistiques` | Statistiques |
| `GET` | `/admin/logs` | Logs scraping |

---

## 🧭 Pages et routage

### Pages publiques
| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Page d'accueil avec présentation |
| `/register` | Register | Création de compte |
| `/login` | Login | Connexion |

### Dashboard utilisateur (rôle `utilisateur`)
| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | DashbordUI | Dashboard avec chatbot |
| `/dashboard/discussion` | DiscussionPage | Nouvelle discussion |
| `/dashboard/discussion/:id` | DiscussionPage | Reprendre une discussion |
| `/dashboard/historique` | HistoriquePage | Historique des conversations |
| `/dashboard/aides-recommandees` | AidesRecommandeesPage | Aides recommandées |
| `/dashboard/profil` | Profile | Gestion du profil |
| `/dashboard/changer-mot-de-passe` | ChangePassword | Changement mot de passe |

### Dashboard administrateur (rôle `administrateur`)
| Route | Page | Description |
|-------|------|-------------|
| `/admin` | AdminDashboard | Dashboard admin |
| `/admin/utilisateurs` | AdminUsers | Gestion utilisateurs |
| `/admin/aides` | AdminAides | Gestion des aides |
| `/admin/sources` | AdminSources | Gestion des sources |
| `/admin/statistiques` | AdminStats | Statistiques |
| `/admin/profil` | Profile | Gestion du profil |
| `/admin/changer-mot-de-passe` | ChangePassword | Changement mot de passe |

---

## 🤖 Chatbot — Streaming SSE

Le chatbot utilise un système de **streaming en temps réel** via Server-Sent Events (SSE) :

### Cycle de vie d'un message

1. **Envoi** du message → état `isThinking = true` (TypingIndicator visible)
2. **Premier chunk** reçu → `isThinking = false`, `isStreaming = true` (bulle IA apparaît et grandit)
3. **Streaming** → les tokens s'affichent progressivement
4. **Événement "done"** → `isStreaming = false`, suggestions + recommendations mises à jour

### Hook `useStreamingChat`

```javascript
const {
  streamingText,    // Texte accumulé
  isThinking,       // En attente du 1er chunk
  isStreaming,      // Chunks en cours
  streamError,      // Erreur éventuelle
  startStream,      // Démarre le stream
  cancelStream,     // Annule le stream
} = useStreamingChat()
```

### Architecture

```
Message → POST /dashboard/chat/stream
              │
              ▼
         SSE Stream
              │
     ┌────────┴────────┐
     │  "chunk" events  │  → streamingText (affichage progressif)
     │  "done" event    │  → metadata (suggestions, recommendations)
     └─────────────────┘
```

---

## 🔐 Authentification

- **JWT** stocké dans `localStorage` après connexion
- **Intercepteur Axios** : injection automatique du token Bearer dans chaque requête
- **Intercepteur 401** : déconnexion automatique + redirection vers `/login`
- **ProtectedRoute** : vérifie l'authentification et le rôle avant d'afficher une page
- **GuestRoute** : redirige les utilisateurs connectés vers leur dashboard
- **3 statuts de compte** : `actif`, `desactive_utilisateur`, `suspendu_admin`

### Contexte Auth (`AuthContext`)
- Fournit : `user`, `token`, `isAuthenticated`, `role`, `authLoading`
- Actions : `login()`, `register()`, `logout()`

### Contexte Profile (`ProfileContext`)
- Fournit : `profile`, `profileLoading`
- Actions : `refreshProfile()`, `updateProfile()`

### Contexte Toast (`ToastContext`)
- Fournit : `showToast()`
- Types : `success`, `error`, `info`

---

## 🎨 Design et UI

- **Mobile-first** avec Tailwind CSS v4
- **ShadCN UI** basé sur Radix (composants accessibles)
- **Typographie** : Geist (via @fontsource)
- **Icônes** : Lucide React
- **Animations** : Framer Motion

---

## 🧗 Difficultés rencontrées

### Streaming SSE
- Gestion du cycle de vie (thinking → streaming → done) avec des états React
- Annulation du stream en cours lors d'un nouveau message ou du démontage du composant
- Différence entre l'état "thinking" (pas encore de réponse) et "streaming" (premiers tokens reçus)

### URL API dynamique
- L'auto-détection de l'URL API (même hôte que le navigateur) est essentielle pour les tests mobiles
- Complexité supplémentaire : détecter si l'URL configurée est locale ou réseau, et ignorer localhost sur mobile

### Routage par rôle
- Deux dashboards distincts (utilisateur / admin) partagent certaines pages (profil, mot de passe)
- Gestion des redirections après connexion selon le rôle
- Protection des routes admin contre les utilisateurs standard

### Interface chatbot
- Affichage fluide des messages pendant le streaming sans re-rendu complet
- Gestion de l'historique contextuel pour la reprise de conversation
- Suggestions dynamiques qui changent selon l'état de la conversation

---

## 🗺️ Roadmap

### Court terme
- [ ] Page de détails d'une aide spécifique
- [ ] Filtres de recherche avancés
- [ ] Amélioration du responsive mobile

### Moyen terme
- [ ] Export PDF des aides
- [ ] Graphiques dashboard (Recharts)
- [ ] Tests E2E (Playwright)

### Long terme
- [ ] Support multilingue (arabe)
- [ ] Progressive Web App (PWA)
- [ ] Mode hors-ligne

---

## 👥 Auteurs

- **ISSAD Dembele** — Développeur full-stack

Projet développé dans le cadre du cycle ingénieur 3II (3ème année).

---

## 📄 Licence

Projet éducatif — AidFinder.