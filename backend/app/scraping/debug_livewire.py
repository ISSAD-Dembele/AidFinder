"""
Debug: test Livewire 3 pagination with raw snapshot.
"""
import requests, re, json, html as html_module
from app.scraping.sources.anapec.emploi import _extract_wire_snapshot, START_URL, _HEADERS, _extract_offers_from_snapshot

s = requests.Session()
r = s.get(START_URL, headers=_HEADERS, timeout=15)
print(f"GET: {r.status_code}")

# Extract raw snapshot from HTML
snap_match = re.search(r'wire:snapshot="([^"]+)"', r.text)
raw_snapshot = html_module.unescape(snap_match.group(1))
snap = _extract_wire_snapshot(r.text)
print(f"Snapshot found: {bool(snap)}")
print(f"Checksum: {snap.get('checksum', '')[:40]}...")

# Extract Livewire 3 config
script_match = re.search(r'<script[^>]+data-csrf="([^"]+)"[^>]+data-update-uri="([^"]+)"', r.text, re.I)
csrf, update_uri = script_match.groups()
print(f"Update URI: {update_uri}")

# Option 1: send raw snapshot
payload = {
    "_token": csrf,
    "components": [{"snapshot": raw_snapshot, "updates": {}, "calls": [{"path": "", "method": "gotoPage", "params": [2]}]}]
}
headers = {**_HEADERS, "Content-Type": "application/json", "Accept": "application/json", "X-Livewire": "true", "X-CSRF-TOKEN": csrf, "Referer": START_URL, "X-Requested-With": "XMLHttpRequest"}
r2 = s.post(update_uri, json=payload, headers=headers, timeout=15)
print(f"POST (raw snapshot): {r2.status_code}")
if r2.status_code == 200:
    data = r2.json()
    ns = json.loads(html_module.unescape(data['components'][0]['snapshot']))
    offers = _extract_offers_from_snapshot(ns)
    print(f"Page 2 offers: {len(offers)}")
    if offers:
        print(f"First: {offers[0].get('intitule_poste')}")
else:
    print(f"Response: {r2.text[:300]}")