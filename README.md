# AidFinder

Plateforme web intelligente de recherche d'aides sociales au Maroc, propulsée par un **chatbot IA conversationnel** avec recommandations personnalisées.

---

## 📋 Présentation

### Objectif
AidFinder est une plateforme qui aide les citoyens marocains à découvrir les aides financières et sociales auxquelles ils peuvent prétendre, via un assistant conversationnel intelligent et une interface moderne.

### Problématique
Au Maroc, l'information sur les aides sociales est dispersée entre plusieurs organismes publics (ANAPEC, OFPPT, CNSS, etc.). Les citoyens ignorent souvent l'existence de ces aides ou ne savent pas comment vérifier leur éligibilité. Les démarches administratives sont complexes et décourageantes.

### Solution proposée
AidFinder centralise les données d'aides via du **scraping automatique** et offre une **expérience conversationnelle** où l'utilisateur dialogue avec un chatbot IA qui :
1. Collecte progressivement son profil (ville, âge, études, situation, handicap)
2. Calcule des **recommandations personnalisées** avec un score de compatibilité
3. L'oriente vers les aides les plus pertinentes
4. S'enrichit automatiquement via le scraping de sources officielles

---

## ✅ Fonctionnalités

### ✅ Terminées
- Authentification complète (inscription, connexion, JWT)
- Gestion des rôles (utilisateur / administrateur)
- Profil utilisateur (consultation, modification, photo, mot de passe)
- Désactivation volontaire du compte
- Suspension admin des comptes
- Chatbot IA conversationnel avec LLM (OpenRouter + Qwen fallback)
- Streaming SSE des réponses du chatbot en temps réel
- Détection d'intention (emploi, études, logement, santé, etc.)
- Collecte progressive du profil via la conversation
- Moteur de recommandations personnalisées (score sur 100)
- Enrichissement des réponses du chatbot avec les recommandations
- Scraping automatique des actualités ANAPEC
- Planificateur de scraping (toutes les 6h)
- Historique des conversations chatbot
- Reprise d'une conversation existante
- Recherche d'aides
- Catégories d'aides
- Dashboard administrateur complet (statistiques, utilisateurs, aides, sources, logs)
- CRUD complet des aides (admin)
- Gestion des utilisateurs (admin)
- Upload photo de profil
- Design responsive (mobile-first)
- Interface en français

### 🚧 En cours
- Robustesse du streaming LLM (timeouts, reconnexion)
- Sources de scraping supplémentaires
- Page de détails d'une aide
- Filtres de recherche avancés

### 📅 Prévues
- Export PDF des aides recommandées
- Notifications push (nouvelles aides)
- Dashboard avec graphiques (Recharts)
- Support multilingue (français, arabe)
- Tests automatisés complets
- CI/CD et déploiement Docker
- Mode PWA (Progressive Web App)

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        AidFinder                               │
│                                                                │
│  ┌─────────────────────┐     ┌─────────────────────┐          │
│  │     Frontend        │     │      Backend        │          │
│  │   React 19 + Vite   │◄───►│   FastAPI + Python  │          │
│  │   Tailwind + ShadCN │     │   SQLAlchemy + PGSQL│          │
│  └─────────────────────┘     └──────────┬──────────┘          │
│                                         │                      │
│                               ┌─────────┴─────────┐           │
│                               │     Services       │           │
│                               │  ┌───────────────┐ │           │
│                               │  │ Chatbot IA    │ │           │
│                               │  │ (LLM + Brain) │ │           │
│                               │  ├───────────────┤ │           │
│                               │  │ Recommandations│ │           │
│                               │  ├───────────────┤ │           │
│                               │  │ Scraping      │ │           │
│                               │  │ (ANAPEC, etc.)│ │           │
│                               │  └───────────────┘ │           │
│                               └─────────────────────┘           │
└────────────────────────────────────────────────────────────────┘
```

### Frontend
Application React 19 avec Vite 8, Tailwind CSS v4 et ShadCN UI. Interface conversationnelle avec streaming SSE pour le chatbot. Voir [frontend/README.md](frontend/README.md).

### Backend
API REST FastAPI avec PostgreSQL, SQLAlchemy, JWT/OAuth2, scraping (BeautifulSoup4) et client LLM (OpenRouter + Qwen). Voir [backend/README.md](backend/README.md).

### Base de données
PostgreSQL avec 15 tables : utilisateurs, aides, catégories, sources, discussions, historiques, résultats chatbot, consultations, logs scraping, notifications, exports, administrateurs, etc.

### IA (Chatbot)
Architecture **LLM-first** avec 3 niveaux de fallback :
1. **OpenRouter** (modèle gratuit configurable)
2. **Qwen DashScope** (fallback)
3. **Moteur conversationnel local** (réponses pré-définies)

### Scraping
- **Source actuelle** : ANAPEC (actualités emploi)
- **Fréquence** : toutes les 6h
- **Mécanisme** : BeautifulSoup4 + requests
- **Architecture extensible** (ajout facile de nouvelles sources)

### Authentification
JWT (python-jose) + OAuth2 Bearer + bcrypt (passlib). 3 statuts de compte.

### Streaming
SSE (Server-Sent Events) pour les réponses temps réel du chatbot. Hook React `useStreamingChat` avec états "thinking" → "streaming" → "done".

### API
RESTful, documentée automatiquement via Swagger (`/docs`).

---

## 🛠️ Stack technique

### Frontend
| Technologie | Rôle |
|-------------|------|
| React 19 | Framework UI |
| Vite 8 | Bundler |
| Tailwind CSS v4 | Framework CSS |
| ShadCN UI (Radix) | Composants UI |
| React Router v7 | Routage |
| Axios | Client HTTP |
| Framer Motion | Animations |
| Lucide React | Icônes |

### Backend
| Technologie | Rôle |
|-------------|------|
| Python 3.12 | Langage |
| FastAPI 0.136 | Framework web |
| Uvicorn 0.48 | Serveur ASGI |
| PostgreSQL | Base de données |
| SQLAlchemy 2.0 | ORM |
| Pydantic 2.13 | Validation |
| python-jose | JWT |
| passlib + bcrypt | Hash mots de passe |
| httpx / requests | Clients HTTP |
| BeautifulSoup4 | Scraping HTML |
| schedule | Planification scraping |

---

## 📁 Structure du projet

```
AidFinder/
├── backend/                    # API FastAPI + PostgreSQL
│   ├── app/
│   │   ├── core/               # Configuration, JWT, sécurité
│   │   ├── database/           # Connexion BDD
│   │   ├── models/             # Modèles SQLAlchemy (15 tables)
│   │   ├── routes/             # Routes API (auth, users, home, dashboard, admin)
│   │   ├── schemas/            # Schémas Pydantic
│   │   ├── services/           # Logique métier (chatbot, scraping, recommandations)
│   │   ├── scraping/           # Système de scraping (ANAPEC)
│   │   ├── main.py             # Point d'entrée FastAPI
│   │   └── create_tables.py    # Initialisation BDD
│   ├── tests/                  # Tests
│   ├── uploads/profiles/       # Photos de profil
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── frontend/                   # Interface React + Vite
│   ├── src/
│   │   ├── components/         # Composants UI et métier
│   │   ├── contexts/           # Contextes React (Auth, Profile, Toast)
│   │   ├── hooks/              # Hooks (streaming, admin, dashboard)
│   │   ├── layouts/            # Layouts (public, dashboard, admin)
│   │   ├── pages/              # Pages (Home, Login, Register, Dashboard, Admin...)
│   │   ├── services/           # Services API (Axios)
│   │   └── utils/              # Utilitaires
│   ├── .env.example
│   ├── package.json
│   └── README.md
├── docs/                       # Documentation du projet
│   ├── maquettes/              # Maquettes UI (PNG)
│   ├── uml/                    # Diagrammes UML (Use Case, Classe)
│   ├── achitecture/            # Diagrammes d'architecture
│   ├── planning/               # Diagramme de Gantt
│   └── Livrable/               # Rapports
└── README.md                   # Ce fichier
```

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- PostgreSQL
- Node.js 18+
- npm

### 1. Cloner le projet

```bash
git clone https://github.com/ISSAD-Dembele/AidFinder.git
cd AidFinder
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env       # Éditer avec vos valeurs
python -m app.create_tables
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend (dans un autre terminal)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 4. Accès

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Documentation API | http://localhost:8000/docs |

---

## 🔐 Variables d'environnement

### Backend (`backend/.env`)
Voir la documentation complète dans [backend/README.md](backend/README.md#variables-denvironnement).

Variables principales :
- `DATABASE_URL` — connexion PostgreSQL
- `SECRET_KEY` — clé JWT
- `OPENROUTER_API_KEY` — clé API OpenRouter (LLM principal)
- `QWEN_API_KEY` — clé API Qwen (fallback LLM)
- `CORS_ORIGINS` — origines autorisées

### Frontend (`frontend/.env`)
| Variable | Description | Défaut |
|----------|-------------|--------|
| `VITE_API_URL` | URL API (optionnel) | Auto-détection |
| `VITE_API_PORT` | Port backend | `8000` |

---

## 🤖 Chatbot IA

### Fonctionnement

1. L'utilisateur envoie un message → `ConversationBrain` détecte l'intention
2. `ResponseGenerator` interroge le LLM (OpenRouter → Qwen → fallback)
3. **Étape 1** : le LLM répond naturellement (sans recommandations)
4. **Étape 2** : si le profil est complet → `RecommendationEngine` calcule les scores
5. **Étape 3** : le LLM réécrit sa réponse en intégrant les aides recommandées
6. La réponse est streamée au frontend via SSE

### Flux de données

```
Message → IntentDetector → LLM (réponse initiale) → 
  └── si profil complet → RecommendationEngine → LLM (réponse enrichie) → 
    → Sauvegarde BDD → Streaming SSE → Frontend
```

### État actuel
✅ Chatbot conversationnel fonctionnel avec LLM  
✅ Streaming SSE opérationnel  
✅ Recommandations calculées et intégrées  
✅ Fallback sans LLM fonctionnel  
🚧 Fiabilité dépendante des API LLM gratuites

---

## 🕷️ Scraping

### Source actuelle
| Source | Type | Données |
|--------|------|---------|
| ANAPEC | Organisme public | Actualités emploi et insertion |

### Fonctionnement
- Démarrage immédiat au lancement du serveur
- Planification : toutes les 6 heures
- Architecture extensible (ajout d'une source = 1 fichier + 1 ligne dans `SCRAPERS`)

---

## 🧗 Difficultés rencontrées

### OpenRouter et modèles gratuits
Les modèles gratuits ont des rate limits stricts et des timeouts fréquents. Solution : fallback vers Qwen puis moteur local.

### Streaming LLM
Implementation SSE avec `httpx.AsyncClient` nécessitant une gestion fine des timeouts, signaux `[DONE]` et lignes non-JSON.

### Intégration IA + Recommandations
Faire collaborer le LLM avec le moteur de scoring sans que l'IA n'invente des aides. Solution en 3 étapes : réponse libre → calcul → enrichissement.

### Collecte de profil depuis le langage naturel
Extraction d'informations (ville, âge, études) depuis des expressions variées. Double approche : regex + LLM.

### CORS et accès mobile
Support du développement local et des tests depuis un téléphone sur le même réseau. Regex dynamique pour les IP privées.

---

## 🗺️ Roadmap

### Court terme
- [ ] Sources scraping : OFPPT, CNSS, CAF Maroc
- [ ] Robustesse streaming LLM
- [ ] Page détails d'une aide
- [ ] Tests unitaires et d'intégration

### Moyen terme
- [ ] Export PDF
- [ ] Notifications push
- [ ] Graphiques dashboard (Recharts)
- [ ] Support arabe

### Long terme
- [ ] CI/CD (GitHub Actions)
- [ ] Déploiement Docker
- [ ] Cache Redis
- [ ] PWA
- [ ] WebSockets

---

## 📄 Documentation

- [Backend README](backend/README.md) — API, installation, configuration
- [Frontend README](frontend/README.md) — Interface, composants, streaming
- [Maquettes UI](docs/maquettes/) — Design de l'interface
- [Diagrammes UML](docs/uml/) — Use Case, Diagramme de classes
- [Architecture](docs/achitecture/) — Diagramme système
- [Planning](docs/planning/) — Diagramme de Gantt
- [Rapport Livrable 1](docs/Livrable/Rapport%20du%20Livrable1%203II-A.pdf)

---

## 👥 Auteurs

- **ISSAD Dembele** — Développeur full-stack

Projet développé dans le cadre du cycle ingénieur **3II** (3ème année).

---

## 📄 Licence

Projet éducatif — AidFinder.