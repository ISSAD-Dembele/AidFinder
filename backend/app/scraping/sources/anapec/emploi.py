"""
Scraper des offres d'emploi ANAPEC.

Point d'entrée exclusif : https://anapec.ma/chercheurs/offres

Fonctionnement :
  - Le site utilise Laravel Livewire 3 pour rendre les offres.
  - La page HTML contient un attribut wire:snapshot avec un JSON
    qui embarque la première page d'offres (15 offres) ainsi que
    les informations de pagination (total pages, page suivante).
  - Les pages suivantes sont récupérées via des requêtes POST
    vers /livewire/message/pages::chercheurs.offres.
  - Les informations de détail d'une offre (description, contrat,
    etc.) sont accessibles via des appels internes depuis anapec.ma.
  - Le point d'entrée unique et exclusif est https://anapec.ma.

Architecture calquée sur news.py, compatible avec manager.py,
scheduler.py, storage.py, normalizer.py, utils.py et BaseScraper.
"""

from app.scraping.utils import (
    sleep_random, log_scraping_error,
)
from app.scraping.normalizer import normalize_record
import requests
import re
import json
import html as html_module


# ── Constantes ─────────────────────────────────────────────────
BASE_URL = "https://anapec.ma"
START_URL = "https://anapec.ma/chercheurs/offres"
LIVEWIRE_ENDPOINT = "https://anapec.ma/livewire/message/pages::chercheurs.offres"
SOURCE_NAME = "ANAPEC"
SOURCE_TYPE = "Organisme public"
CATEGORY_NAME = "Offres d'emploi"
MAX_PAGES = 1000  # sécurité
# Nombre d'offres par page (observé dans le snapshot Livewire)
OFFERS_PER_PAGE = 15


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
}


def _extract_wire_snapshot(html_text: str) -> dict | None:
    """Extrait le wire:snapshot du composant pages::chercheurs.offres.

    Args:
        html_text: HTML complet de la page.

    Returns:
        Le dictionnaire JSON du snapshot, ou None si non trouvé.
    """
    # Chercher le snapshot qui contient le composant offres
    pattern = r'wire:snapshot="([^"]+)"'
    matches = re.findall(pattern, html_text)

    for raw_snap in matches:
        decoded = html_module.unescape(raw_snap)
        try:
            data = json.loads(decoded)
            if data.get("memo", {}).get("name") == "pages::chercheurs.offres":
                return data
        except (json.JSONDecodeError, TypeError):
            continue

    return None


def _extract_offers_from_snapshot(snapshot: dict) -> list[dict]:
    """Extrait la liste des offres depuis le snapshot Livewire.

    Les offres se trouvent dans data.latestOffers[0].
    Chaque offre contient les clés :
        id, ref_offre, date_offre, intitule_poste, entreprise, lieu_travail

    Args:
        snapshot: Dictionnaire du snapshot Livewire.

    Returns:
        Liste des dictionnaires d'offres.
    """
    latest_offers = snapshot.get("data", {}).get("latestOffers", [])
    if isinstance(latest_offers, list) and len(latest_offers) > 0:
        offers = latest_offers[0]
        if isinstance(offers, list):
            return offers
    return []


def _extract_pagination_info(snapshot: dict) -> dict:
    """Extrait les informations de pagination depuis le snapshot.

    Les infos se trouvent dans data.paginate[0].
    Contient : count (total offres), last (dernière page), next (page suivante).

    Args:
        snapshot: Dictionnaire du snapshot Livewire.

    Returns:
        Dictionnaire avec total_offers et total_pages.
    """
    info = {"total_offers": 0, "total_pages": 1}

    paginate = snapshot.get("data", {}).get("paginate", [])
    if isinstance(paginate, list) and len(paginate) > 0:
        pag_data = paginate[0]
        if isinstance(pag_data, dict):
            count = pag_data.get("count", "0")
            info["total_offers"] = int(count) if count else 0

            last_url = pag_data.get("last", "")
            if last_url:
                match = re.search(r"page:(\d+)", str(last_url))
                if match:
                    info["total_pages"] = int(match.group(1))

    return info


def _extract_component_id(snapshot: dict) -> str | None:
    """Extrait l'identifiant du composant Livewire depuis le snapshot.

    Returns:
        L'ID du composant, ou None si non trouvé.
    """
    return snapshot.get("memo", {}).get("id")


def _extract_csrf_token(html_text: str) -> str | None:
    """Extrait le token CSRF depuis la page HTML.

    Args:
        html_text: HTML complet de la page.

    Returns:
        Le token CSRF, ou None si non trouvé.
    """
    match = re.search(
        r'<meta\s+name="csrf-token"\s+content="([^"]+)"',
        html_text,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _fetch_page(
    page: int,
    csrf_token: str,
    cookies: dict,
    component_id: str,
    fingerprint: dict,
) -> dict | None:
    """Récupère une page d'offres via l'API Livewire.

    Args:
        page: Numéro de la page à récupérer.
        csrf_token: Token CSRF.
        cookies: Cookies de session.
        component_id: ID du composant Livewire.
        fingerprint: Fingerprint du composant (sans l'ID).

    Returns:
        La réponse JSON du Livewire, ou None en cas d'échec.
    """
    headers = {
        "User-Agent": _HEADERS["User-Agent"],
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Livewire": "true",
        "X-CSRF-TOKEN": csrf_token,
        "Referer": START_URL,
        "X-Requested-With": "XMLHttpRequest",
    }

    livewire_fingerprint = {
        "id": component_id,
        "name": fingerprint.get("name", "pages::chercheurs.offres"),
        "path": fingerprint.get("path", "chercheurs/offres"),
        "method": "GET",
    }

    payload = {
        "fingerprint": livewire_fingerprint,
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": "",
            "data": [],
            "dataMeta": [],
            "checksum": fingerprint.get("checksum", ""),
        },
        "updates": [
            {
                "type": "callMethod",
                "payload": {"method": "gotoPage", "params": [page]},
            }
        ],
    }

    try:
        response = requests.post(
            LIVEWIRE_ENDPOINT,
            json=payload,
            headers=headers,
            cookies=cookies,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_scraping_error(f"anapec_emploi_livewire_page_{page}", str(e))
        return None


def fetch_total_pages() -> int:
    """Récupère le nombre total de pages disponibles.

    Returns:
        Nombre total de pages (au moins 1).
    """
    try:
        response = requests.get(START_URL, headers=_HEADERS, timeout=15)
        response.raise_for_status()
        snapshot = _extract_wire_snapshot(response.text)
        if not snapshot:
            print("[ANAPEC-EMPLOI] Impossible d'extraire le snapshot Livewire.")
            return 1
        info = _extract_pagination_info(snapshot)
        print(f"[ANAPEC-EMPLOI] Total offres : {info['total_offers']}, "
              f"pages : {info['total_pages']}")
        return info["total_pages"]
    except Exception as e:
        log_scraping_error("anapec_emploi_total_pages", str(e))
        return 1


def fetch_listings() -> list[dict]:
    """Récupère toutes les offres d'emploi via Livewire.

    1. Télécharge la page initiale (page 1, déjà dans le snapshot).
    2. Extrait les infos de pagination.
    3. Parcourt les pages suivantes via des requêtes POST Livewire.

    Returns:
        Liste des dictionnaires bruts d'offres (infos de base).
    """
    all_offers: list[dict] = []

    # ── 1. Page initiale ──────────────────────────────────────
    print(f"[ANAPEC-EMPLOI] Téléchargement de {START_URL}")
    try:
        response = requests.get(START_URL, headers=_HEADERS, timeout=15)
        response.raise_for_status()
        html_text = response.text
        cookies = response.cookies
    except Exception as e:
        log_scraping_error("anapec_emploi_init", str(e))
        print(f"[ANAPEC-EMPLOI] Erreur accès à {START_URL}: {e}")
        return all_offers

    # Extraire le snapshot
    snapshot = _extract_wire_snapshot(html_text)
    if not snapshot:
        print("[ANAPEC-EMPLOI] Aucun snapshot Livewire trouvé.")
        return all_offers

    # Extraire les offres de la page 1
    page_offers = _extract_offers_from_snapshot(snapshot)
    all_offers.extend(page_offers)
    print(f"[ANAPEC-EMPLOI] Page 1 : {len(page_offers)} offres")

    # Infos de pagination
    info = _extract_pagination_info(snapshot)
    total_pages = info["total_pages"]
    print(f"[ANAPEC-EMPLOI] Pages totales : {total_pages}")

    # Extraire le CSRF token
    csrf_token = _extract_csrf_token(html_text)
    if not csrf_token:
        print("[ANAPEC-EMPLOI] Aucun token CSRF trouvé.")
        return all_offers

    # Extraire l'ID du composant et le fingerprint
    component_id = _extract_component_id(snapshot)
    if not component_id:
        print("[ANAPEC-EMPLOI] Aucun ID de composant trouvé.")
        return all_offers

    # Préparer le fingerprint de base
    fingerprint = snapshot.get("memo", {})

    # ── 2. Pages suivantes ────────────────────────────────────
    page = 1
    while page < total_pages and page < MAX_PAGES:
        page += 1
        sleep_random(2, 4)

        print(f"[ANAPEC-EMPLOI] Page {page}/{total_pages}...")
        livewire_data = _fetch_page(
            page, csrf_token, cookies, component_id, fingerprint
        )

        if not livewire_data:
            print(f"[ANAPEC-EMPLOI] Échec page {page}, arrêt.")
            break

        # La réponse Livewire contient un nouveau snapshot
        new_snapshot = livewire_data.get("components", [{}])[0].get("snapshot", "")
        if new_snapshot:
            try:
                new_data = json.loads(html_module.unescape(new_snapshot))
                page_offers = _extract_offers_from_snapshot(new_data)
                if not page_offers:
                    print(f"[ANAPEC-EMPLOI] Page {page} vide, arrêt.")
                    break
                all_offers.extend(page_offers)
                print(f"[ANAPEC-EMPLOI] Page {page} : {len(page_offers)} offres "
                      f"(total : {len(all_offers)})")

                # Mettre à jour l'ID du composant (peut changer)
                new_id = _extract_component_id(new_data)
                if new_id:
                    component_id = new_id

                # Mise à jour du checksum
                new_checksum = new_data.get("checksum")
                if new_checksum:
                    fingerprint["checksum"] = new_checksum
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"[ANAPEC-EMPLOI] Erreur parsing page {page}: {e}")
                break
        else:
            print(f"[ANAPEC-EMPLOI] Réponse Livewire vide pour page {page}, arrêt.")
            break

    print(f"[ANAPEC-EMPLOI] Total offres récupérées : {len(all_offers)}")
    return all_offers


def parse_listing(offer_data: dict) -> dict | None:
    """Convertit une offre brute du snapshot en enregistrement normalisé.

    Les offres depuis le snapshot Livewire contiennent les champs :
        id, ref_offre, date_offre, intitule_poste, entreprise, lieu_travail

    Args:
        offer_data: Dictionnaire brut d'une offre depuis le snapshot.

    Returns:
        Enregistrement normalisé prêt pour la sauvegarde,
        ou None si les données sont invalides.
    """
    if not offer_data or not isinstance(offer_data, dict):
        return None

    offer_id = offer_data.get("id")
    titre = offer_data.get("intitule_poste")
    lieu = (offer_data.get("lieu_travail") or "").strip()
    reference = offer_data.get("ref_offre")
    entreprise = offer_data.get("entreprise")
    date_offre = offer_data.get("date_offre")

    if not offer_id or not titre:
        return None

    # URL officielle (point d'entrée anapec.ma)
    url_officielle = f"{BASE_URL}/chercheurs/offres"

    # Construire la description à partir du titre et du lieu
    description = f"{titre}"
    if lieu:
        description += f" - {lieu}"
    if entreprise and entreprise not in ("-", "", None):
        # Si entreprise ressemble à une URL (logo), on la nettoie
        if not entreprise.startswith("http"):
            description += f" - {entreprise}"

    # Pour les détails complets, on utilise l'ID comme référence
    # Les informations détaillées (type_contrat, formation, etc.)
    # ne sont pas disponibles directement depuis anapec.ma.
    # On utilise les données de base du snapshot.

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
        "description": description,
        "date_limite": None,
        "type_aide": "Offre d'emploi",
        "montant": None,
        "age_min": None,
        "age_max": None,
        "region_cible": lieu or "Maroc",
        "niveau_etude_requis": None,
        "statut_socio_pro_requis": None,
        "handicap_requis": False,
        "url_officielle": url_officielle,
        "image_url": None,
        # Champs supplémentaires
        "reference_offre": reference,
        "entreprise_nom": entreprise if entreprise and entreprise != "-" else None,
        "date_publication": date_offre,
        "lieu_travail": lieu,
    }

    return normalize_record(data)


def scrape_emploi():
    """Lance le scraping complet des offres d'emploi ANAPEC.

    Point d'entrée exclusif : https://anapec.ma/chercheurs/offres.
    Fonction principale appelée par le manager.
    Suit le même schéma que scrape_news().

    Returns:
        Liste des enregistrements normalisés.
    """
    print("[ANAPEC-EMPLOI] Début du scraping des offres d'emploi")
    records = []

    try:
        # 1. Récupérer toutes les offres via Livewire
        offers = fetch_listings()
        print(f"[ANAPEC-EMPLOI] {len(offers)} offres à traiter")

        # 2. Pour chaque offre, normaliser
        for i, offer in enumerate(offers, 1):
            print(f"[ANAPEC-EMPLOI] Traitement offre {i}/{len(offers)}")
            record = parse_listing(offer)
            if record:
                records.append(record)

            # Pause pour éviter la surcharge
            if i % 10 == 0:
                sleep_random(2, 3)
            else:
                sleep_random(0.5, 1.5)

    except Exception as e:
        log_scraping_error("anapec_emploi", str(e))
        print(f"[ANAPEC-EMPLOI] Erreur : {e}")

    print(f"[ANAPEC-EMPLOI] {len(records)} enregistrements récupérés")
    return records