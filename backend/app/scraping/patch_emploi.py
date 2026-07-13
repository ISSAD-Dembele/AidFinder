"""
Script de correction du scraper emploi.py
Applique les 4 correctifs nécessaires pour Livewire 3.
"""
import re

with open('app/scraping/sources/anapec/emploi.py', 'r') as f:
    c = f.read()

# 1. Ajouter LIVEWIRE_UPDATE_ENDPOINT
c = c.replace(
    'LIVEWIRE_ENDPOINT = "https://anapec.ma/livewire/message/pages::chercheurs.offres"',
    'LIVEWIRE_ENDPOINT = "https://anapec.ma/livewire/message/pages::chercheurs.offres"\nLIVEWIRE_UPDATE_ENDPOINT = "https://anapec.ma/livewire-568c8989/update"'
)

# 2. Remplacer _extract_csrf_token (meta -> script data-csrf)
old_csrf = '''def _extract_csrf_token(html_text: str) -> str | None:
    """Extrait le token CSRF depuis la page HTML.

    Args:
        html_text: HTML complet de la page.

    Returns:
        Le token CSRF, ou None si non trouvé.
    """
    match = re.search(
        r'<meta\\s+name="csrf-token"\\s+content="([^"]+)"',
        html_text,
        re.IGNORECASE,
    )
    return match.group(1) if match else None'''

new_csrf = '''def _extract_csrf_token(html_text: str) -> str | None:
    """Extrait le token CSRF depuis la page HTML.

    Args:
        html_text: HTML complet de la page.

    Returns:
        Le token CSRF, ou None si non trouvé.
    """
    match = re.search(
        r'<script[^>]+data-csrf="([^"]+)"[^>]+data-update-uri="([^"]+)"',
        html_text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return None'''

c = c.replace(old_csrf, new_csrf)

# 3. Remplacer _extract_offers_from_snapshot (dépaquetage Livewire 3)
old_extract = '''def _extract_offers_from_snapshot(snapshot: dict) -> list[dict]:
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
    return []'''

new_extract = '''def _extract_offers_from_snapshot(snapshot: dict) -> list[dict]:
    """Extrait la liste des offres depuis le snapshot Livewire.

    Les offres se trouvent dans data.latestOffers sous la forme :
        latestOffers = [
            [ [offre, {"s":"arr"}], [offre, {"s":"arr"}] ],
            {"s":"arr"}
        ]

    Args:
        snapshot: Dictionnaire du snapshot Livewire.

    Returns:
        Liste des dictionnaires d'offres.
    """
    latest_offers = snapshot.get("data", {}).get("latestOffers", [])
    if not isinstance(latest_offers, list) or len(latest_offers) == 0:
        return []

    page_wrappers = latest_offers[0]
    if not isinstance(page_wrappers, list):
        return []

    offers = []
    for item in page_wrappers:
        if isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict):
            offers.append(item[0])
    return offers'''

c = c.replace(old_extract, new_extract)

# 4. Remplacer _fetch_page (Livewire 2 -> Livewire 3)
old_fetch = '''def _fetch_page(
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
        return None'''

new_fetch = '''def _fetch_page(
    page: int,
    csrf_token: str,
    cookies: dict,
    component_id: str,
    fingerprint: dict,
) -> dict | None:
    """Récupère une page d'offres via l'API Livewire 3.

    Args:
        page: Numéro de la page à récupérer.
        csrf_token: Token CSRF.
        cookies: Cookies de session.
        component_id: ID du composant Livewire.
        fingerprint: Fingerprint du composant (snapshot memo).

    Returns:
        La réponse JSON du Livewire, ou None en cas d'échec.
    """
    headers = {
        "User-Agent": _HEADERS["User-Agent"],
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Livewire": "true",
        "Referer": START_URL,
        "X-Requested-With": "XMLHttpRequest",
    }

    payload = {
        "_token": csrf_token,
        "components": [
            {
                "snapshot": json.dumps(
                    {
                        "memo": {
                            "id": component_id,
                            "name": fingerprint.get("name", "pages::chercheurs.offres"),
                            "path": fingerprint.get("path", "chercheurs/offres"),
                            "method": "GET",
                        },
                        "data": {},
                        "checksum": fingerprint.get("checksum", ""),
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "updates": {},
                "calls": [
                    {
                        "path": "",
                        "method": "gotoPage",
                        "params": [page],
                    }
                ],
            }
        ],
    }

    try:
        response = requests.post(
            LIVEWIRE_UPDATE_ENDPOINT,
            json=payload,
            headers=headers,
            cookies=cookies,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_scraping_error(f"anapec_emploi_livewire_page_{page}", str(e))
        return None'''

c = c.replace(old_fetch, new_fetch)

# 5. Fix snapshot parsing in the loop (str or dict)
c = c.replace(
    '                new_data = json.loads(html_module.unescape(new_snapshot))',
    '                if isinstance(new_snapshot, str):\n                    new_data = json.loads(html_module.unescape(new_snapshot))\n                else:\n                    new_data = new_snapshot'
)

with open('app/scraping/sources/anapec/emploi.py', 'w') as f:
    f.write(c)

print("OK - 5 patches applied successfully")