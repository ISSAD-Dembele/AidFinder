import logging, re, time, random, requests


from urllib.parse import urljoin
from bs4 import BeautifulSoup

#logger du module
logger = logging.getLogger(__name__)

def request_with_retry(url, headers=None, retries=3, timeout=10):
    "effectue une requête HTTP avec des tentatives en cas d'échec"
    if headers is None:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning("Tentative %s/%s échouée pour l'URL: %s", attempt + 1, retries, url)
            if attempt == retries - 1:
                raise e
            time.sleep(2 * (attempt + 1))

def get_soup(url, headers=None):
    "Telecharge une page puis retourne son objet BeautifulSoup"
    response = request_with_retry(url, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')
    
def clean_text(text):
    "Nettoie le texte en supprimant les espaces superflus et les caractères spéciaux"
    if not text:
        return ''
    text = clean_whitespace(text)  # remplace les espaces multiples par un seul espace
    return text
def clean_whitespace(text):
    "supprime les espaces multiples"
    if not text:
        return ''
    return " ".join(text.split())
    
def clean_date(date_string):
    "nettoie et formate une date"
    if not date_string:
        return None
    date_string = clean_text(date_string)
    return date_string
    
def clean_amount(amount):
    "extrait uniquement les nombres d'un montant"
    if not amount:
        return None
    amount = re.sub(r"[^\d]", "", amount)
    if amount == "":
        return None
    return int(amount)
    
def extract_absolute_url(base_url, relative_url):
    "Construit une URL absolue"
    return urljoin(base_url, relative_url)
    
def is_valid_url(url):
    "Vérifie si une URL est valide"
    return bool(url) and url.startswith(('http://', 'https://'))
    
def sleep_random(min_seconds=1, max_seconds=3):
    "Fait une pause aléatoire entre min_seconds et max_seconds"
    time.sleep(random.uniform(min_seconds, max_seconds))
    
def log_scraping_error(source, error):
    "journalise une erreur de scraping"
    logger.error("[%s] Erreur de scraping: %s", source, str(error))