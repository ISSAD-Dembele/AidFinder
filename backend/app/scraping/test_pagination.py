"""
Test simple de pagination Livewire 3.
Execute le scraping avec MAX_PAGES=5 pour verifier la pagination.
"""
import sys, json
sys.path.insert(0, '.')

from app.scraping.sources.anapec.emploi import (
    fetch_listings, _extract_livewire_config, 
    _extract_wire_snapshot, START_URL, _HEADERS
)
import requests
import app.scraping.sources.anapec.emploi as m
m.MAX_PAGES = 5

print('='*60)
print('TEST PAGINATION LIVEWIRE 3')
print('='*60)

offers = fetch_listings()
print(f'\nTotal offres recuperees: {len(offers)}')
print(f'Pages parcourues (MAX_PAGES=5): attendu ~75 offres (5x15)')

if offers:
    print(f'\nPremiere offre: {json.dumps(offers[0], ensure_ascii=False, indent=2)[:300]}')
    print(f'\nurl_officielle sera: https://anapec.ma/chercheurs/offres')
    
    # Verifier qu'aucune n'a www.anapec.org
    anapec_org = [o for o in offers if 'www.anapec.org' in str(o)]
    print(f'\nOffres avec www.anapec.org: {len(anapec_org)} (attendu: 0)')
else:
    print('\nAucune offre recuperee.')
    # Debug : test l'extraction de config Livewire
    r = requests.get(START_URL, headers=_HEADERS, timeout=15)
    csrf, uri = _extract_livewire_config(r.text)
    snap = _extract_wire_snapshot(r.text)
    print(f'CSRF: {csrf}')
    print(f'Update URI: {uri}')
    print(f'Snapshot: {bool(snap)}')