import requests
import json

ERPNEXT_URL = 'http://127.0.0.1:8081'
HEADERS = {'Host': 'erpnext.local'}

session = requests.Session()
session.headers.update(HEADERS)
session.post(f'{ERPNEXT_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'KsbioAdmin2026'})

# Check Companies
resp = session.get(f'{ERPNEXT_URL}/api/resource/Company')
print(f'Companies status: {resp.status_code}')
if resp.status_code == 200:
    data = json.loads(resp.text).get('data', [])
    print(f'Found {len(data)} companies:')
    for c in data:
        print(f'  {c.get("name")}: {c.get("company_name")}')
else:
    print(f'Response: {resp.text[:300]}')

# Check what account types are valid
resp2 = session.get(f'{ERPNEXT_URL}/api/resource/Account Type')
print(f'\nAccount Types status: {resp2.status_code}')
if resp2.status_code == 200:
    data = json.loads(resp2.text).get('data', [])
    print(f'Found {len(data)} account types:')
    for t in data[:10]:
        print(f'  {t.get("name")}')
