# AidFinder — Backend

API REST développée avec **FastAPI** pour la plateforme AidFinder.  
Le backend gère l'authentification, le chatbot IA conversationnel, le scraping d'aides sociales, les recommandations personnalisées et l'administration de la plateforme.

---

## 📋 Présentation

### Objectif
Fournir une API robuste et scalable qui alimente l'interface utilisateur AidFinder, permettant aux citoyens marocains de découvrir les aides financières et sociales auxquelles ils sont éligibles via un assistant conversationnel intelligent.

### Problématique
Au Maroc, de nombreuses aides sociales existent (emploi, logement, santé, études, entrepreneuriat) mais les citoyens peinent à les connaître et à savoir s'ils y sont éligibles. L'information est dispersée entre plusieurs organismes publics.

### Solution proposée
Un backend unifié qui :
- Centralise les données d'aides via du **scraping automatique** de sources officielles
- Offre un **chatbot IA** (OpenRouter + Qwen en fallback) qui dialogue naturellement avec l'utilisateur
- Calcule des **recommandations personnalisées** basées sur le profil de l'utilisateur (ville, âge, études, situation, handicap)
- Diffuse les réponses en **streaming SSE** pour une expérience temps réel
- Fournit une **API REST complète** pour l'authentification, le dashboard, l'administration

---

## ✅ Fonctionnalités

### ✅ Terminées
- Authentification complète (inscription, connexion, JWT, OAuth2 Bearer)
- Gestion des rôles (utilisateur / administrateur)
- Profil utilisateur (consultation, modification, upload photo, changement mot de passe)
- Désactivation volontaire du compte
- Suspension admin des comptes
- Chatbot IA conversationnel avec LLM (OpenRouter + Qwen)
- Streaming SSE des réponses du chatbot
- Détection d'intention (emploi, études, logement, santé, etc.)
- Collecte progressive du profil via la conversation
- Moteur de recommandations personnalisées (score sur 100)
- Enrichissement des réponses du chatbot avec les recommandations
- Scraping automatique des actualités ANAPEC
- Planificateur de scraping (exécution toutes les 6h)
- Dashboard administrateur (statistiques, logs, utilisateurs, aides, sources)
- CRUD complet des aides (admin)
- Gestion des utilisateurs (admin)
- Consultation et historique des discussions
- Recherche d'aides
- Catégories d'aides
- CORS configurable (développement local + réseau local)

### 🚧 En cours
- Amélioration de la robustesse du streaming (gestion des timeouts, reconnexion)
- Support de sources de scraping supplémentaires
- Export PDF des résultats

### 📅 Prévues
- Notifications push
- Export PDF des aides recommandées
- Dashboard avec graphiques avancés
- Support multilingue (français, arabe)
- Tests automatisés complets
- CI/CD

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Routes   │  │ Services │  │  Models   │  │  Scraping  │  │
│  │  (API)    │→│ (Métier) │→│ (SQLAlch.)│  │  (Sources) │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│       │              │              │              │        │
│       ▼              ▼              ▼              ▼        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgreSQL (Base de données)            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  LLM Client (OpenRouter → Qwen → Fallback)          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Frontend
Application React (Vite) qui consomme l'API REST. Voir [frontend/README.md](../frontend/README.md).

### Backend
API REST FastAPI avec architecture en couches :
- **Routes** : points d'entrée HTTP
- **Services** : logique métier
- **Models** : modèles SQLAlchemy (ORM)
- **Schemas** : validation Pydantic
- **Core** : configuration, sécurité, utilitaires

### Base de données
PostgreSQL avec SQLAlchemy ORM. Tables principales :
- `utilisateurs` — comptes utilisateurs
- `aides` — aides financières et sociales
- `categories_aides` — catégories d'aides
- `sources_aides` — sources des données
- `discussions` — messages du chatbot
- `historiques` — sessions de conversation
- `resultats_chatbots` — recommandations générées
- `consultations_aides` — historique des consultations
- `scraping_logs` — logs du scraping
- `administrateurs` — administrateurs
- `notifications` — notifications utilisateur
- `exports_pdf` — exports PDF
- `documents_requis` — documents nécessaires pour les aides

### IA (Chatbot)
- **Primary** : OpenRouter (modèle configurable, ex: `qwen/qwen3-30b-a3b:free`)
- **Fallback** : Qwen via DashScope API
- **Fallback ultime** : moteur de conversation local (réponses pré-définies)
- **Streaming** : SSE (Server-Sent Events) pour les réponses en temps réel
- **Détection d'intention** : regex patterns + contexte conversationnel
- **Collecte de profil** : extraction automatique depuis les messages + LLM

### Scraping
- **Source actuelle** : ANAPEC (Agence Nationale de Promotion de l'Emploi et des Compétences)
- **Fréquence** : toutes les 6 heures (exécution immédiate au démarrage)
- **Mécanisme** : BeautifulSoup4 + requests
- **Stockage** : normalisation et déduplication avant insertion en base

### Authentification
- JWT (JSON Web Tokens) avec python-jose
- OAuth2 Bearer token
- Hash des mots de passe avec bcrypt (passlib)
- 3 statuts de compte : `actif`, `desactive_utilisateur`, `suspendu_admin`

### Streaming
- SSE (Server-Sent Events) via `StreamingResponse` FastAPI
- Le chatbot stream les tokens un par un depuis le LLM
- Le frontend affiche progressivement la réponse (effet "typing")

### API
RESTful, documentée automatiquement via Swagger (`/docs`) et ReDoc (`/redoc`).

---

## 🛠️ Stack technique

| Technologie | Rôle |
|-------------|------|
| **Python 3.12** | Langage |
| **FastAPI 0.136** | Framework web |
| **Uvicorn 0.48** | Serveur ASGI |
| **PostgreSQL** | Base de données |
| **SQLAlchemy 2.0** | ORM |
| **Pydantic 2.13** | Validation des données |
| **python-jose** | JWT (JSON Web Tokens) |
| **passlib + bcrypt** | Hash des mots de passe |
| **httpx** | Client HTTP asynchrone (streaming LLM) |
| **requests** | Client HTTP synchrone (LLM, scraping) |
| **BeautifulSoup4** | Parsing HTML (scraping) |
| **schedule** | Planificateur de tâches (scraping) |
| **python-dotenv** | Variables d'environnement |
| **python-multipart** | Upload de fichiers |
| **email-validator** | Validation des emails |

---

## 📁 Structure du projet

```
backend/
├── app/
│   ├── core/                  # Configuration, sécurité, utilitaires
│   │   ├── config.py          # Variables d'environnement
│   │   ├── securite.py        # JWT, hash, OAuth2
│   │   ├── datetime_utils.py  # Utilitaires de date
│   │   └── statuts_compte.py  # Gestion des statuts
│   ├── database/
│   │   ├── database.py        # Connexion PostgreSQL (engine, session)
│   │   └── session.py         # Dépendance FastAPI get_db
│   ├── models/                # Modèles SQLAlchemy (15 tables)
│   │   ├── utilisateurs.py
│   │   ├── aides.py
│   │   ├── categorie_aide.py
│   │   ├── source_aide.py
│   │   ├── discussion.py
│   │   ├── historique.py
│   │   ├── resultat_chat.py
│   │   ├── consultation_aide.py
│   │   ├── scraping_logs.py
│   │   ├── administrateur.py
│   │   ├── notification.py
│   │   ├── export_pdf.py
│   │   ├── export_resultat.py
│   │   ├── document_requis.py
│   │   └── action_moderation.py
│   ├── routes/                # Routes FastAPI
│   │   ├── auth.py            # /auth (register, login, deactivate)
│   │   ├── users.py           # /users (profil, photo, password)
│   │   ├── home.py            # /api/home (aides, stats, catégories, search)
│   │   ├── dashboard.py       # /dashboard (chat, history, recommendations)
│   │   └── admin.py           # /admin (users, aides, sources, logs, stats)
│   ├── schemas/               # Schémas Pydantic
│   │   ├── utilisateur.py
│   │   ├── token.py
│   │   ├── chat.py
│   │   ├── home.py
│   │   ├── dashboard.py
│   │   └── admin.py
│   ├── services/              # Logique métier
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── compte_service.py
│   │   ├── home_service.py
│   │   ├── dashboard_service.py
│   │   ├── admin_service.py
│   │   ├── chat_service.py         # Orchestrateur du chatbot
│   │   ├── conversation_brain.py   # Détection d'intention + collecte profil
│   │   ├── conversation_engine.py  # Machine à états + métadonnées
│   │   ├── response_generator.py   # Génération de réponses (LLM + fallback)
│   │   ├── llm_client.py           # Client LLM (OpenRouter + Qwen)
│   │   └── recommendation_engine.py # Moteur de scoring des aides
│   ├── scraping/              # Système de scraping
│   │   ├── base_scraper.py    # Classe abstraite
│   │   ├── manager.py         # Orchestrateur des scrapers
│   │   ├── scheduler.py       # Planificateur (toutes les 6h)
│   │   ├── normalizer.py      # Normalisation des données
│   │   ├── storage.py         # Stockage en base
│   │   ├── utils.py           # Utilitaires HTTP
│   │   └── sources/
│   │       └── anapec/
│   │           └── news.py    # Scraper ANAPEC
│   ├── create_tables.py       # Script d'initialisation BDD
│   └── main.py                # Point d'entrée FastAPI
├── tests/
│   └── test_chat_service.py
├── uploads/
│   └── profiles/              # Photos de profil uploadées
├── .env.example               # Exemple de configuration
├── requirements.txt           # Dépendances Python
└── README.md
```

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- PostgreSQL (local ou distant)
- npm (pour le frontend)

### 1. Cloner le projet

```bash
git clone https://github.com/ISSAD-Dembele/AidFinder.git
cd AidFinder/backend
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# ou : venv\Scripts\activate  (Windows)
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditer le fichier `.env` avec vos propres valeurs (voir section [Variables d'environnement](#variables-denvironnement)).

### 5. Initialiser la base de données

```bash
python -m app.create_tables
```

### 6. Lancer le serveur

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur :
- **Local** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc

### 7. Lancer le frontend (dans un autre terminal)

```bash
cd ../frontend
npm install
npm run dev
```

---

## 🔐 Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:password@localhost:5432/aidfinder` |
| `SECRET_KEY` | Clé secrète pour signer les JWT | — (obligatoire) |
| `ALGORITHM` | Algorithme de signature JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité du token (minutes) | `30` |
| `HOST` | Adresse d'écoute du serveur | `0.0.0.0` |
| `PORT` | Port d'écoute du serveur | `8000` |
| `CORS_ORIGINS` | Origines CORS autorisées (séparées par des virgules) | `http://localhost:5173,http://127.0.0.1:5173` |
| `CORS_ORIGIN_REGEX` | Regex pour les IP privées (réseau local) | Regex par défaut pour 192.168.x.x, 10.x.x.x, 172.16-31.x.x |
| `OPENROUTER_API_KEY` | Clé API OpenRouter (LLM principal) | — (optionnel, recommandé) |
| `OPENROUTER_API_URL` | URL API OpenRouter | `https://openrouter.ai/api/v1/chat/completions` |
| `OPENROUTER_MODEL` | Modèle OpenRouter | `qwen/qwen3-30b-a3b:free` |
| `OPENROUTER_MAX_TOKENS` | Nombre max de tokens (réponse) | `700` |
| `OPENROUTER_TEMPERATURE` | Température du modèle | `0.2` |
| `OPENROUTER_TIMEOUT_SECONDS` | Timeout des requêtes OpenRouter | `30` |
| `OPENROUTER_SITE_URL` | URL du site (header OpenRouter) | `http://localhost:5173` |
| `OPENROUTER_SITE_NAME` | Nom du site (header OpenRouter) | `AidFinder` |
| `QWEN_API_KEY` | Clé API Qwen DashScope (fallback LLM) | — (optionnel) |
| `QWEN_API_URL` | URL API Qwen DashScope | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions` |
| `QWEN_MODEL` | Modèle Qwen | `qwen-plus` |
| `QWEN_MAX_TOKENS` | Nombre max de tokens (réponse) | `700` |
| `QWEN_TEMPERATURE` | Température du modèle | `0.2` |
| `QWEN_TIMEOUT_SECONDS` | Timeout des requêtes Qwen | `30` |

> **Note** : Les clés API ne sont pas incluses dans le dépôt. Créez un compte sur [OpenRouter](https://openrouter.ai/) et/ou [DashScope](https://dashscope.aliyun.com/) pour obtenir vos propres clés. Le chatbot fonctionne également sans LLM (mode fallback avec réponses pré-définies).

---

## 📡 API — Routes principales

### Authentification (`/auth`)

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| POST | `/auth/register` | Inscription utilisateur | Non |
| POST | `/auth/login` | Connexion (retourne JWT) | Non |
| PATCH | `/auth/deactivate` | Désactivation volontaire du compte | Oui |

### Utilisateurs (`/users`)

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/users/me` | Consultation du profil | Oui |
| PATCH | `/users/me` | Modification du profil | Oui |
| PATCH | `/users/change-password` | Changement du mot de passe | Oui |
| PATCH | `/users/photo` | Upload photo de profil (jpg, jpeg, png, webp, heic) | Oui |

### Accueil (`/api/home`)

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/home/latest-aids` | 6 aides les plus récentes | Non |
| GET | `/api/home/stats` | Statistiques (nb aides, sources, mise à jour) | Non |
| GET | `/api/home/categories` | Catégories d'aides avec nombre d'aides | Non |
| GET | `/api/home/search?q=` | Recherche dans les aides | Non |
| POST | `/api/home/aids/{id}/consultation` | Enregistrer une consultation | Oui |

### Dashboard utilisateur (`/dashboard`)

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/dashboard` | Dashboard utilisateur (stats, dernières aides) | Oui |
| GET | `/dashboard/history` | Historique des conversations | Oui |
| GET | `/dashboard/history/{id}` | Détail d'une conversation (messages + recommandations) | Oui |
| DELETE | `/dashboard/history/{id}` | Supprimer une conversation | Oui |
| POST | `/dashboard/chat` | Envoyer un message au chatbot (synchrone) | Oui |
| POST | `/dashboard/chat/stream` | Envoyer un message au chatbot (streaming SSE) | Oui |
| POST | `/dashboard/chat/{id}/consultation/{aide_id}` | Enregistrer consultation depuis le chat | Oui |
| GET | `/dashboard/recommendations` | Aides recommandées pour l'utilisateur | Oui |
| GET | `/dashboard/recent-aids` | Aides consultées récemment | Oui |
| GET | `/dashboard/stats` | Statistiques utilisateur | Oui |

### Administration (`/admin`)

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/admin/dashboard` | Statistiques globales de la plateforme | Admin |
| GET | `/admin/utilisateurs` | Liste des utilisateurs | Admin |
| GET | `/admin/utilisateur/{id}` | Détail d'un utilisateur | Admin |
| PUT | `/admin/utilisateur/{id}` | Modifier un utilisateur | Admin |
| PATCH | `/admin/utilisateur/{id}/activer` | Activer un utilisateur | Admin |
| PATCH | `/admin/utilisateur/{id}/desactiver` | Désactiver un utilisateur | Admin |
| DELETE | `/admin/utilisateur/{id}` | Supprimer un utilisateur | Admin |
| GET | `/admin/aides` | Liste des aides | Admin |
| POST | `/admin/aides` | Créer une aide | Admin |
| PUT | `/admin/aides/{id}` | Modifier une aide | Admin |
| DELETE | `/admin/aides/{id}` | Supprimer une aide | Admin |
| PATCH | `/admin/aides/{id}/activer` | Activer une aide | Admin |
| PATCH | `/admin/aides/{id}/desactiver` | Désactiver une aide | Admin |
| GET | `/admin/sources` | Liste des sources | Admin |
| POST | `/admin/sources/{id}/scraping` | Relancer le scraping d'une source | Admin |
| GET | `/admin/statistiques` | Statistiques détaillées | Admin |
| GET | `/admin/logs` | Logs du scraping | Admin |

---

## 🤖 Chatbot IA

### Architecture

Le chatbot suit une architecture **LLM-first** avec fallback progressif :

```
Message utilisateur
       │
       ▼
┌──────────────────┐
│ ConversationBrain │ ← Détection d'intention + collecte profil
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ ResponseGenerator │ ← LLM (OpenRouter → Qwen → Fallback)
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│ RecommendationEngine │ ← Scoring après réponse (si profil complet)
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Enrichissement LLM   │ ← Réécriture de la réponse avec les aides
└──────────────────────┘
```

### ConversationBrain

- **IntentDetector** : détecte l'intention via regex (emploi, études, logement, santé, etc.)
- **ProfileCollector** : extrait les informations du profil depuis les messages (ville, âge, études, etc.) via regex + LLM
- **StateMachine** : machine à états (GREETING → COLLECTING_INFO → DISCUSSING → CLARIFYING)

### LLM Client

- **Primary** : OpenRouter (modèle gratuit configurable, ex: `qwen/qwen3-30b-a3b:free`)
- **Fallback** : Qwen via DashScope API
- **Fallback ultime** : `ConversationFallback` — réponses pré-définies basées sur l'état et l'intention

### Streaming

- Les réponses sont diffusées en **SSE** (Server-Sent Events)
- Le frontend reçoit les tokens un par un et les affiche progressivement
- Support du streaming pour OpenRouter et Qwen

### Recommandations

- Calculées **après** la réponse LLM initiale
- Score sur 100 basé sur : région, niveau d'étude, statut socio-pro, âge, handicap
- Si le profil est complet et pertinent → une seconde requête LLM enrichit la réponse avec les aides
- Les recommandations sont persistées dans `resultats_chatbots`

### État actuel

✅ Le chatbot conversationnel avec LLM est **fonctionnel**  
✅ Le streaming SSE est **opérationnel**  
✅ Les recommandations sont **calculées et intégrées** dans les réponses  
✅ Le fallback sans LLM **fonctionne** (réponses pré-définies)  
🚧 La fiabilité du streaming dépend de la disponibilité des API LLM gratuites  
🚧 Les timeouts OpenRouter peuvent nécessiter des ajustements

---

## 🕷️ Scraping

### Source actuelle

| Source | Type | URL | Données collectées |
|--------|------|-----|-------------------|
| **ANAPEC** | Organisme public | https://anapec.ma/blog/posts | Actualités, programmes d'emploi et d'insertion |

### Fonctionnement

1. **Démarrage** : le scraping s'exécute immédiatement au lancement du serveur
2. **Planification** : répété automatiquement toutes les 6 heures
3. **Processus** :
   - Récupération des pages HTML via `requests` + `BeautifulSoup4`
   - Extraction des données (titre, description, lien, image)
   - Normalisation des champs
   - Sauvegarde en base avec déduplication (via `content_hash`)
   - Logging des résultats (succès/échec) dans `scraping_logs`
4. **Architecture extensible** : ajout d'une nouvelle source = créer un fichier dans `sources/` et l'ajouter à la liste `SCRAPERS` dans `manager.py`

---

## 🧗 Difficultés rencontrées

### OpenRouter et modèles gratuits
- Les modèles gratuits sur OpenRouter (comme `qwen/qwen3-30b-a3b:free`) ont des **rate limits** stricts et des **timeouts fréquents**
- Solution : implémentation d'un **fallback** vers Qwen DashScope, puis vers un moteur de conversation local
- Le système retente automatiquement avec le fournisseur suivant en cas d'échec

### Streaming LLM
- L'implémentation du streaming SSE avec `httpx.AsyncClient` a nécessité une gestion fine des timeouts et des erreurs de connexion
- Les réponses streaming doivent être parsées au format SSE (`data: {...}\n\n`)
- Gestion des signaux `[DONE]` et des lignes non-JSON

### Intégration IA
- Faire collaborer le LLM avec le moteur de recommandations sans que l'un n'écrase l'autre
- Solution en 3 étapes : 1) LLM répond librement → 2) Backend calcule les scores → 3) LLM réécrit sa réponse avec les aides
- Éviter que le LLM n'invente des aides qui n'existent pas dans la base

### Collecte de profil
- Extraction des informations depuis le langage naturel (expressions variées, fautes, argot)
- Double approche : regex pour les cas simples + LLM pour les cas complexes
- Maintien de l'état de la conversation entre les messages

### CORS et accès mobile
- Configuration CORS pour supporter à la fois le développement local et les tests depuis un téléphone sur le réseau local
- Regex dynamique pour les IP privées

---

## 🗺️ Roadmap

### Court terme
- [ ] Ajouter des sources de scraping supplémentaires (CAF Maroc, OFPPT, etc.)
- [ ] Améliorer la gestion des timeouts et retries du LLM
- [ ] Tests unitaires et d'intégration complets
- [ ] Documentation API avec exemples concrets

### Moyen terme
- [ ] Export PDF des aides recommandées
- [ ] Notifications push (nouvelles aides disponibles)
- [ ] Dashboard admin avec graphiques (Chart.js / Recharts)
- [ ] Support multilingue (français, arabe)

### Long terme
- [ ] CI/CD (GitHub Actions)
- [ ] Déploiement Docker
- [ ] Cache Redis pour les réponses LLM fréquentes
- [ ] WebSockets pour le chat temps réel

---

## 👥 Auteurs

- **ISSAD Dembele** — Développeur full-stack

Projet développé dans le cadre du cycle ingénieur 3II (3ème année).

---

## 📄 Licence

Projet éducatif — AidFinder.