from app.scraping.utils import(
    get_soup, clean_text,
    extract_absolute_url,
    sleep_random,log_scraping_error)

from app.scraping.normalizer import normalize_record

BASE_URL = "https://anapec.ma"
START_URL = "https://anapec.ma/blog/posts"
SOURCE_NAME = "ANAPEC"
SOURCE_TYPE = "Organisme public"
CATEGORY_NAME = "Emploi et insertion"

def fetch_listings():
    """Récupère toutes les actualités ANAPEC."""

    all_listings = []
    page = 1
    MAX_PAGES = 100
    previous_first_title = None

    while page <= MAX_PAGES:
        url = f"{START_URL}?page={page}"
        print(f"[ANAPEC] Lecture de la page {page}")

        try:
            soup = get_soup(url)
        except Exception:
            break

        listings = soup.select(".th-blog.blog-single")

        if not listings:
            break

        # Évite une boucle infinie si la dernière page est répétée
        first_title_element = listings[0].select_one("h2.blog-title")
        first_title = (
            clean_text(first_title_element.get_text())
            if first_title_element
            else None
            )

        if first_title == previous_first_title:
            print("[ANAPEC] Dernière page atteinte.")
            break

        previous_first_title = first_title

        print(f"   -> {len(listings)} articles")

        all_listings.extend(listings)

        sleep_random(1, 2)
        page += 1

    print(f"[ANAPEC] Total : {len(all_listings)} articles")

    return all_listings

def parse_listing(listing):
    "extrait les informations d'une anapec"
    title_element = listing.select_one("h2.blog-title")
    description_element = listing.select_one("p.blog-text")
    link_element = listing.select_one(".blog-title a")
    image_element = listing.select_one(".blog-img img")

    title = clean_text(title_element.get_text()) if title_element else None
    description = clean_text(description_element.get_text()) if description_element else None

    url = (
    extract_absolute_url(BASE_URL, link_element["href"])
    if link_element else None)

    image = (
    extract_absolute_url(BASE_URL, image_element["src"])
    if image_element else None)
    
    data = {
        "source_nom": SOURCE_NAME,
        "source_url": BASE_URL,
        "source_type": SOURCE_TYPE,
        "source_fiable": True,
        "categorie_nom": CATEGORY_NAME,
        "categorie_description": "Programmes d'emploi, d'insertion professionnelle et d'accompagnement.",
        "titre": title,
        "description": description,
        "date_limite": None,
        "type_aide": "Programme d'insertion",
        "montant": None,
        "age_min": None,
        "age_max": None,
        "region_cible": "Maroc",
        "niveau_etude_requis": None,
        "statut_socio_pro_requis": None,
        "handicap_requis": False,
        "url_officielle": url,
        "image_url": image,
        }
        
    return normalize_record(data)

def scrape_news():
    "Lance le scraping complet de anapec"
    print("[ANAPEC] Début du scraping")
    records = []
    try:
        listings = fetch_listings()
        for listing in listings:
            record = parse_listing(listing)
            if record:
                records.append(record)
            sleep_random()
    except Exception as e:
        log_scraping_error("anapec_news", str(e))
        
    print(f"[ANAPEC] {len(records)} enregistrements récupérés")
    return records
