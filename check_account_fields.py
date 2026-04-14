import requests
import json

ERPNEXT_URL = 'http://127.0.0.1:8081'
HEADERS = {'Host': 'erpnext.local'}

session = requests.Session()
session.headers.update(HEADERS)
session.post(f'{ERPNEXT_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'KsbioAdmin2026'})

# Get Account doctype metadata
resp = session.get(f'{ERPNEXT_URL}/api/method/frappe.desk.form.meta.get_meta?doctype=Account')
print(f'Status: {resp.status_code}')
data = json.loads(resp.text)
fields = data.get('data', {}).get('fields', [])
print('Account fields:')
for f in fields[:30]:
    fname = f.get("fieldname")
    ftype = f.get("fieldtype")
    label = f.get("label")
    print(f'  {fname}: {ftype} ({label})')
