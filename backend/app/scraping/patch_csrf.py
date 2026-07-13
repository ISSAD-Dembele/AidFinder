"""Patch: ajoute X-CSRF-TOKEN header dans _fetch_page"""
with open('app/scraping/sources/anapec/emploi.py', 'r') as f:
    c = f.read()

old = '''        "X-Livewire": "true",
        "Referer": START_URL,
        "X-Requested-With": "XMLHttpRequest",
    }

    payload = {
        "_token": csrf_token,
        "components": ['''

new = '''        "X-Livewire": "true",
        "X-CSRF-TOKEN": csrf_token,
        "Referer": START_URL,
        "X-Requested-With": "XMLHttpRequest",
    }

    payload = {
        "_token": csrf_token,
        "components": ['''

if old in c:
    c = c.replace(old, new)
    with open('app/scraping/sources/anapec/emploi.py', 'w') as f:
        f.write(c)
    print('Patch CSRF OK')
else:
    print('Pattern not found, checking alternatives...')
    # Check if X-CSRF-TOKEN already present
    if 'X-CSRF-TOKEN' in c:
        print('X-CSRF-TOKEN already present - no patch needed')
    else:
        print('ERROR: pattern not found')
        # Debug: show around "X-Livewire"
        import re
        for m in re.finditer(r'X-Livewire.{0,300}', c, re.DOTALL):
            print(repr(m.group()))