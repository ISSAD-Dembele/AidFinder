import time, schedule
from app.scraping.manager import run_all_scrapers

def start_scheduler():
    run_all_scrapers()  # Run scrapers immediately on startup
    schedule.every(6).hours.do(run_all_scrapers)  # Schedule to run every 6 hours
    while True:
        schedule.run_pending()
        time.sleep(30)  # Sleep for 30 seconds before checking again