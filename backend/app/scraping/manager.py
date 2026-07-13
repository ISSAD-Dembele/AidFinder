from app.scraping.sources.anapec import scrape_news, scrape_emploi
from app.scraping.storage import save_records
from app.database.database import SessionLocal
from app.models.scraping_logs import ScrapingLog
from datetime import datetime
from app.core.datetime_utils import utc_now


SCRAPERS = [
    scrape_news,
    scrape_emploi,
]


def _source_name(scraper, records: list) -> str:
    if records:
        return records[0].get("source_nom") or scraper.__name__
    return scraper.__name__


def _save_scraping_log(
    source: str,
    started_at: datetime,
    finished_at: datetime,
    records_count: int,
    status: str,
    error_message: str | None = None,
) -> None:
    db = SessionLocal()
    try:
        duration = str(finished_at - started_at)
        db.add(
            ScrapingLog(
                source=source,
                started_at=started_at,
                finished_at=finished_at,
                duration=duration,
                new_records=records_count,
                updated_records=0,
                expired_records=0,
                status=status,
                error_message=error_message,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def run_all_scrapers():
    "Lance tous les scrapers et retourne une liste de tous les enregistrements"
    all_records = []
    for scraper in SCRAPERS:
        started_at = utc_now()
        try:
            records = scraper()
            save_records(records)
            all_records.extend(records)
            finished_at = utc_now()
            _save_scraping_log(
                source=_source_name(scraper, records),
                started_at=started_at,
                finished_at=finished_at,
                records_count=len(records),
                status="success",
            )
        except Exception as e:
            finished_at = utc_now()
            _save_scraping_log(
                source=scraper.__name__,
                started_at=started_at,
                finished_at=finished_at,
                records_count=0,
                status="error",
                error_message=str(e),
            )
            print(f"Error occurred with {scraper.__name__}: {e}")
    return all_records
