from app.scraping.sources.anapec import scrape_news
from app.scraping.storage import save_records


SCRAPERS = [
    scrape_news,
]

def run_all_scrapers():
    "Lance tous les scrapers et retourne une liste de tous les enregistrements"
    all_records = []
    for scraper in SCRAPERS:
        try:
            records = scraper()
            save_records(records)
            all_records.extend(records)
        except Exception as e:
            print(f"Error occurred with {scraper.__name__}: {e}")
    return all_records