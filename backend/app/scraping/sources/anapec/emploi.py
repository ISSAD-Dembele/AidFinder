"""
Scraper des offres d'emploi ANAPEC.

Récupère toutes les offres d'emploi depuis l'API JSON de www.anapec.org,
puis enrichit chaque offre avec les détails complets depuis la page d'annonce.

Utilise le pipeline de scraping existant :
    - utils.py : requêtes HTTP, BeautifulSoup, nettoyage
    - normalizer.py : normalisation des champs et génération content_hash
    - storage.py : sauvegarde en base de données
    - manager.py : orchestration et logging
    - scheduler.py : exécution périodique

Architecture calquée sur news.py.
"""

import warnings
from app.scraping.utils import (
    clean_text,
    extract_absolute_url,
    sleep_random, log_scraping_error,
)
from app.scraping.normalizer import normalize_record
from bs4 import BeautifulSoup
import requests
import re
import json


# Supprimer le warning urllib3 pour les requêtes verify=False
# vers www.anapec.org (certificat GoGetSSL non reconnu)
warnings.filterwarnings(
    "ignore",
    message="Unverified HTTPS request is being made",
    category=requests.packages.urllib3.exceptions.InsecureRequestWarning,
)

# ── Constantes ─────────────────────────────────────────────────
BASE_URL = "https://anapec.ma"
API_BASE_URL = "https://www.anapec.org"
START_URL = "https://anapec.ma/chercheurs/offres"
API_URL_TEMPLATE = (
    "https://www.anapec.org"
    "/sigec-app-rv/chercheurs/resultat_recherche_json"
    "/page:{page}/tout:all/language:fr"
)
DETAIL_URL_TEMPLATE = (
    "https://www.anapec.org"
    "/sigec-app-rv/fr/entreprises/bloc_offre_home/{offer_id}/display"
)
SOURCE_NAME = "ANAPEC"
SOURCE_TYPE = "Organisme public"
CATEGORY_NAME = "Offres d'emploi"
MAX_PAGES = 1000  # sécurité


# Le certificat SSL présenté par www.anapec.org n'est pas reconnu
# par le bundle certifi de Python (GoGetSSL).
# Le site est néanmoins légitime et utilisé officiellement par l'ANAPEC.
# La désactivation de la vérification SSL est limitée exclusivement
# à ce domaine afin de permettre le scraping.
_ANAPEC_ORG_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
}


def _anapec_request_with_retry(
    url: str,
    headers: dict | None = None,
    retries: int = 3,
    timeout: int = 10,
) -> requests.Response:
    """Requête HTTP vers www.anapec.org avec vérification SSL désactivée.

    Même comportement que request_with_retry() du module utils,
    mais avec verify=False pour contourner le certificat GoGetSSL
    non reconnu par le bundle certifi de Python.

    Args:
        url: URL de la requête.
        headers: En-têtes HTTP supplémentaires.
        retries: Nombre de tentatives.
        timeout: Délai d'attente en secondes.

    Returns:
        Objet Response de requests.

    Raises:
        requests.RequestException: si toutes les tentatives échouent.
    """
    merged_headers = dict(_ANAPEC_ORG_DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)

    for attempt in range(retries):
        try:
            response = requests.get(
                url, headers=merged_headers, timeout=timeout, verify=False,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            log_scraping_error(
                "anapec_emploi_ssl",
                f"Tentative {attempt + 1}/{retries} pour {url}: {e}",
            )
            if attempt == retries - 1:
                raise
            sleep_random(1, 2)


def _anapec_get_soup(url: str, headers: dict | None = None) -> BeautifulSoup:
    """Télécharge une page depuis www.anapec.org et retourne son BeautifulSoup.

    Utilise _anapec_request_with_retry() en interne (verify=False).

    Args:
        url: URL de la page à télécharger.
        headers: En-têtes HTTP supplémentaires.

    Returns:
        Objet BeautifulSoup de la page.
    """
    response = _anapec_request_with_retry(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")


def _fetch_json_api(page: int) -> dict | None:
    """Récupère les résultats d'une page via l'API JSON.

    Args:
        page: Numéro de la page à récupérer (1-indexé).

    Returns:
        Le dictionnaire JSON parsé, ou None en cas d'échec.
    """
    url = API_URL_TEMPLATE.format(page=page)
    try:
        response = _anapec_request_with_retry(
            url,
            headers={
                "Accept": "application/json",
                "Referer": START_URL,
            },
        )
        return response.json()
    except Exception as e:
        log_scraping_error(f"anapec_emploi_api_page_{page}", str(e))
        return None


def _extract_pagination_info(data: dict | None) -> dict:
    """Extrait les informations de pagination depuis la réponse JSON.

    Args:
        data: Données JSON parsées.

    Returns:
        Dictionnaire avec 'current_page', 'total_pages', 'total_offers'.
    """
    info = {"current_page": 1, "total_pages": 1, "total_offers": 0}

    if not data or not isinstance(data, dict):
        return info

    paginate = data.get("paginate")
    if not paginate or not isinstance(paginate, dict):
        return info

    info["total_offers"] = int(paginate.get("count", 0))

    last_url = paginate.get("last", "")
    if last_url:
        match = re.search(r"page:(\d+)", last_url)
        if match:
            info["total_pages"] = int(match.group(1))

    return info


def _extract_offers_from_api(data: dict | None) -> list[dict]:
    """Extrait la liste des offres depuis la réponse JSON de l'API.

    L'API renvoie les offres dans une liste sous la clé 'Offre'.
    Chaque offre est un dict avec les clés :
        id, ref_offre, date_offre, intitule_poste, entreprise, lieu_travail

    Args:
        data: Données JSON parsées.

    Returns:
        Liste des dictionnaires d'offres.
    """
    if not data or not isinstance(data, dict):
        return []

    # L'API renvoie les offres dans une liste sous la clé 'Offre'
    offers = data.get("Offre", [])

    if not isinstance(offers, list):
        return []

    return offers


def fetch_total_pages() -> int:
    """Récupère le nombre total de pages disponibles.

    Returns:
        Nombre total de pages (au moins 1).
    """
    data = _fetch_json_api(1)
    info = _extract_pagination_info(data)
    print(f"[ANAPEC-EMPLOI] Total offres : {info['total_offers']}, "
          f"pages : {info['total_pages']}")
    return info["total_pages"]


def fetch_listings() -> list[dict]:
    """Récupère toutes les offres d'emploi via l'API paginée.

    Parcourt toutes les pages de l'API JSON et agrège les résultats.

    Returns:
        Liste des dictionnaires bruts d'offres (infos de base).
    """
    all_offers: list[dict] = []
    page = 1

    # Récupérer la page 1 qui contient aussi les infos de pagination
    data = _fetch_json_api(page)
    if not data:
        print("[ANAPEC-EMPLOI] Aucune donnée reçue de l'API.")
        return all_offers

    info = _extract_pagination_info(data)
    total_pages = info["total_pages"]
    print(f"[ANAPEC-EMPLOI] Pages totales : {total_pages}")

    # Extraire les offres de la page 1
    page_offers = _extract_offers_from_api(data)
    all_offers.extend(page_offers)
    print(f"[ANAPEC-EMPLOI] Page {page} : {len(page_offers)} offres")

    # Parcourir les pages suivantes
    while page < total_pages and page < MAX_PAGES:
        page += 1
        sleep_random(1, 2)

        data = _fetch_json_api(page)
        if not data:
            print(f"[ANAPEC-EMPLOI] Échec page {page}, arrêt.")
            break

        page_offers = _extract_offers_from_api(data)
        if not page_offers:
            print(f"[ANAPEC-EMPLOI] Page {page} vide, arrêt.")
            break

        all_offers.extend(page_offers)
        print(f"[ANAPEC-EMPLOI] Page {page} : {len(page_offers)} offres "
              f"(total : {len(all_offers)})")

    print(f"[ANAPEC-EMPLOI] Total offres récupérées : {len(all_offers)}")
    return all_offers


def _extract_detail_field(
    soup: BeautifulSoup,
    label: str,
) -> str | None:
    """Extrait un champ depuis la page détail d'une offre.

    Cherche un texte contenant le label (ex: 'Type de contrat :')
    puis retourne la valeur qui suit.

    Args:
        soup: Objet BeautifulSoup de la page détail.
        label: Le texte du label à chercher (ex: 'Type de contrat').

    Returns:
        La valeur extraite, ou None si non trouvée.
    """
    # Stratégie : chercher dans tout le texte du body
    body = soup.find("body")
    if not body:
        return None

    text = body.get_text(separator="\n")

    # Chercher le label dans le texte
    for line in text.split("\n"):
        line_clean = line.strip()
        if label.lower() in line_clean.lower():
            # Retourner tout après le label
            parts = line_clean.split(":", 1)
            if len(parts) > 1:
                value = parts[1].strip()
                if value and len(value) < 500:
                    return value
            # Sinon regarder la ligne suivante
            return None

    return None


def _extract_section_text(
    soup: BeautifulSoup,
    section_title: str,
) -> str | None:
    """Extrait le texte d'une section thématique.

    Cherche un titre de section (ex: 'Description de Poste')
    et retourne le texte jusqu'à la prochaine section.

    Args:
        soup: Objet BeautifulSoup de la page détail.
        section_title: Titre de la section à trouver.

    Returns:
        Texte de la section, ou None si non trouvée.
    """
    body = soup.find("body")
    if not body:
        return None

    text = body.get_text(separator="\n")
    lines = text.split("\n")
    lines_clean = [l.strip() for l in lines if l.strip()]

    in_section = False
    section_lines = []
    section_keywords = [
        "description", "profil", "missions", "compétences",
        "commentaire", "poste", "formation", "expérience",
    ]

    for line in lines_clean:
        if section_title.lower() in line.lower():
            in_section = True
            continue

        if in_section:
            # Détecter si on arrive à une nouvelle section
            is_new_section = False
            for kw in section_keywords:
                if (
                    line.lower().startswith(kw.lower())
                    and line.lower() != section_title.lower()
                ):
                    is_new_section = True
                    break

            if is_new_section and len(section_lines) > 2:
                break

            section_lines.append(line)

    if section_lines:
        return " ".join(section_lines)

    return None


def fetch_detail(offer_id: str) -> BeautifulSoup | None:
    """Récupère la page détail d'une offre.

    Args:
        offer_id: Identifiant numérique de l'offre.

    Returns:
        Objet BeautifulSoup de la page, ou None en cas d'échec.
    """
    url = DETAIL_URL_TEMPLATE.format(offer_id=offer_id)
    try:
        return _anapec_get_soup(url)
    except Exception as e:
        log_scraping_error(f"anapec_emploi_detail_{offer_id}", str(e))
        return None


def parse_detail(soup: BeautifulSoup) -> dict:
    """Parse la page détail pour extraire tous les champs disponibles.

    Args:
        soup: Objet BeautifulSoup de la page détail.

    Returns:
        Dictionnaire avec les champs extraits.
    """
    if not soup:
        return {}

    body = soup.find("body")
    if not body:
        return {}

    full_text = body.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]

    detail = {}

    # ── Informations structurées ──────────────────────────────
    # Référence
    ref_match = re.search(
        r"Référence de l'offre:\s*(\S+)", full_text, re.IGNORECASE
    )
    if ref_match:
        detail["reference"] = ref_match.group(1)

    # Date de publication
    date_match = re.search(r"Date\s*:\s*(\d{2}/\d{2}/\d{4})", full_text)
    if date_match:
        detail["date_offre"] = date_match.group(1)

    # Agence
    agence_match = re.search(r"Agence\s*:\s*(.+)", full_text)
    if agence_match:
        detail["agence"] = agence_match.group(1).strip()

    # Secteur d'activité
    secteur_match = re.search(
        r"Secteur d'activité\s*:\s*(.+)", full_text, re.IGNORECASE
    )
    if secteur_match:
        detail["secteur_activite"] = secteur_match.group(1).strip()

    # Type de contrat
    contrat_match = re.search(
        r"Type de contrat\s*:\s*(.+)", full_text, re.IGNORECASE
    )
    if contrat_match:
        detail["type_contrat"] = contrat_match.group(1).strip()

    # Date de début
    debut_match = re.search(
        r"Date de début\s*:\s*(\d{2}/\d{2}/\d{4})", full_text, re.IGNORECASE
    )
    if debut_match:
        detail["date_debut"] = debut_match.group(1)

    # Lieu de travail
    lieu_match = re.search(
        r"Lieu de travail\s*:\s*(.+)", full_text, re.IGNORECASE
    )
    if lieu_match:
        detail["lieu_travail"] = lieu_match.group(1).strip()

    # Formation
    formation_match = re.search(
        r"Formation\s*:\s*(.+)", full_text, re.IGNORECASE
    )
    if formation_match:
        detail["formation"] = formation_match.group(1).strip()

    # Expérience
    exp_match = re.search(
        r"Expérience professionnelle\s*:\s*(.+)",
        full_text,
        re.IGNORECASE,
    )
    if exp_match:
        detail["experience"] = exp_match.group(1).strip()

    # Poste
    poste_match = re.search(
        r"Poste\s*:\s*(.+)", full_text, re.IGNORECASE
    )
    if poste_match:
        detail["poste"] = poste_match.group(1).strip()

    # Langues
    langues_match = re.search(
        r"Langues\s*:\s*(.+)", full_text, re.IGNORECASE
    )
    if langues_match:
        detail["langues"] = langues_match.group(1).strip()

    # ── Sections textuelles ───────────────────────────────────
    # Description de l'entreprise
    desc_ent = _extract_section_text(soup, "Description de l'entreprise")
    if not desc_ent:
        desc_ent = _extract_section_text(soup, "Description de l’entreprise")
    if desc_ent:
        detail["description_entreprise"] = desc_ent

    # Description du poste
    desc_poste = _extract_section_text(soup, "Description de Poste")
    if desc_poste:
        detail["description_poste"] = desc_poste

    # Caractéristiques du poste / missions
    carac_poste = _extract_section_text(soup, "Caractéristiques du poste")
    if carac_poste:
        detail["missions"] = carac_poste

    # Profil recherché
    profil = _extract_section_text(soup, "Profil recherché")
    if profil:
        detail["profil_recherche"] = profil

    # Description du profil
    desc_profil = _extract_section_text(soup, "Description du profil")
    if desc_profil:
        detail["description_profil"] = desc_profil

    # Commentaire
    commentaire = _extract_section_text(soup, "Commentaire")
    if commentaire:
        detail["commentaire"] = commentaire

    return detail


def parse_listing(offer_data: dict) -> dict | None:
    """Convertit une offre brute de l'API en enregistrement normalisé.

    Args:
        offer_data: Dictionnaire brut d'une offre depuis l'API.

    Returns:
        Enregistrement normalisé prêt pour la sauvegarde,
        ou None si les données sont invalides.
    """
    if not offer_data or not isinstance(offer_data, dict):
        return None

    offer_id = offer_data.get("id")
    titre = offer_data.get("intitule_poste")
    lieu = offer_data.get("lieu_travail", "").strip()
    reference = offer_data.get("ref_offre")
    entreprise = offer_data.get("entreprise")
    date_offre = offer_data.get("date_offre")

    if not offer_id or not titre:
        return None

    # URL officielle
    url_officielle = DETAIL_URL_TEMPLATE.format(offer_id=offer_id)

    # Construire la description à partir du titre et du lieu
    description = f"{titre}"
    if lieu:
        description += f" - {lieu}"
    if entreprise and entreprise != "-":
        description += f" - {entreprise}"

    # Récupérer les détails complets
    print(f"   -> Détail offre {offer_id}...")
    soup = fetch_detail(offer_id)
    detail = parse_detail(soup) if soup else {}

    # Fusionner les données
    data = {
        "source_nom": SOURCE_NAME,
        "source_url": BASE_URL,
        "source_type": SOURCE_TYPE,
        "source_fiable": True,
        "categorie_nom": CATEGORY_NAME,
        "categorie_description": (
            "Offres d'emploi publiées par les employeurs "
            "via l'ANAPEC."
        ),
        "titre": titre,
        "description": detail.get("description_poste")
        or detail.get("missions")
        or description,
        "date_limite": None,  # Pas de date limite explicite
        "type_aide": "Offre d'emploi",
        "montant": None,
        "age_min": None,
        "age_max": None,
        "region_cible": lieu or "Maroc",
        "niveau_etude_requis": detail.get("formation"),
        "statut_socio_pro_requis": None,
        "handicap_requis": False,
        "url_officielle": url_officielle,
        "image_url": None,
        # Champs supplémentaires (conservés dans normalize_record
        # mais accessibles pour le normalizer)
        "reference_offre": reference,
        "entreprise_nom": entreprise if entreprise != "-" else None,
        "secteur_activite": detail.get("secteur_activite"),
        "type_contrat": detail.get("type_contrat"),
        "experience_requise": detail.get("experience"),
        "formation_requise": detail.get("formation"),
        "langues_requises": detail.get("langues"),
        "missions": detail.get("missions"),
        "profil_recherche": detail.get("profil_recherche")
        or detail.get("description_profil"),
        "description_entreprise": detail.get("description_entreprise"),
        "commentaire": detail.get("commentaire"),
        "agence": detail.get("agence"),
        "date_publication": date_offre,
        "lieu_travail": lieu,
    }

    return normalize_record(data)


def scrape_emploi():
    """Lance le scraping complet des offres d'emploi ANAPEC.

    Fonction principale appelée par le manager.
    Suit le même schéma que scrape_news().

    Returns:
        Liste des enregistrements normalisés.
    """
    print("[ANAPEC-EMPLOI] Début du scraping des offres d'emploi")
    records = []

    try:
        # 1. Récupérer toutes les offres via l'API paginée
        offers = fetch_listings()
        print(f"[ANAPEC-EMPLOI] {len(offers)} offres à traiter")

        # 2. Pour chaque offre, récupérer les détails et normaliser
        for i, offer in enumerate(offers, 1):
            print(f"[ANAPEC-EMPLOI] Traitement offre {i}/{len(offers)}")
            record = parse_listing(offer)
            if record:
                records.append(record)

            # Pause entre chaque détail pour éviter la surcharge
            if i % 5 == 0:
                sleep_random(2, 4)
            else:
                sleep_random(1, 2)

    except Exception as e:
        log_scraping_error("anapec_emploi", str(e))
        print(f"[ANAPEC-EMPLOI] Erreur : {e}")

    print(f"[ANAPEC-EMPLOI] {len(records)} enregistrements récupérés")
    return records