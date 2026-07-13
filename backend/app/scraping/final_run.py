"""
Execution finale : scraping ANAPEC + sauvegarde + verification.
"""
import sys, json
from datetime import datetime
from sqlalchemy import text
sys.path.insert(0, '.')

from app.scraping.sources.anapec.emploi import scrape_emploi
from app.scraping.storage import save_records
from app.database.database import SessionLocal
import app.scraping.sources.anapec.emploi as m

# Limiter a 5 pages pour un test rapide
m.MAX_PAGES = 5

print('=' * 70)
print('NOUVEAU SCRAPING ANAPEC - EXECUTION FINALE')
print('Point d entree : https://anapec.ma/chercheurs/offres')
print('=' * 70)

start = datetime.now()
records = scrape_emploi()
elapsed = (datetime.now() - start).total_seconds()

print()
print('=' * 70)
print(f'RESULTATS : {len(records)} enregistrements normalises en {elapsed:.1f}s')
print('=' * 70)

if records:
    save_records(records)
    print(f'{len(records)} enregistrements sauvegardes en base.')
    
    print()
    print('15 PREMIERES LIGNES INSEREES :')
    print('-' * 90)
    for i, rec in enumerate(records[:15], 1):
        titre = (rec.get('titre') or '')[:53]
        url = rec.get('url_officielle') or ''
        print(f'  {i:>2}. {titre:<53} | {url}')
    
    bad = [r for r in records if 'www.anapec.org' in (r.get('url_officielle') or '')]
    print()
    print(f'VERIF www.anapec.org dans url_officielle : {len(bad)} (attendu: 0)')
    if not bad:
        print('  OK - aucune URL de l ancien scraper')
    
    db = SessionLocal()
    try:
        logs = db.execute(text(
            'SELECT source, status, new_records, duration '
            'FROM scraping_logs ORDER BY started_at DESC LIMIT 3'
        )).fetchall()
        print()
        print('DERNIERS LOGS DE SCRAPING :')
        for log in logs:
            print(f'  [{log[1]:>7}] {log[0]:<30} | {log[2]} enreg. | {log[3]}')
        
        total = db.execute(text('SELECT COUNT(*) FROM aides')).scalar()
        old = db.execute(text(
            "SELECT COUNT(*) FROM aides "
            "WHERE url_officielle LIKE '%www.anapec.org%' "
            "OR url_officielle LIKE '%sigec-app-rv%'"
        )).scalar()
        print()
        print('TABLE AIDES APRES SCRAPING :')
        print(f'  Total aides : {total}')
        print(f'  Ancien scraper (www.anapec.org) : {old} (doit etre 0)')
        if old == 0:
            print('  ✅ BASE PROPRE - Aucune trace de l ancien scraper')
    finally:
        db.close()
else:
    print('Aucun enregistrement recupere.')

print()
print('=' * 70)
print('PROCESSUS TERMINE AVEC SUCCES')
print('=' * 70)