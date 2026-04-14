import requests
import json

ERPNEXT_URL = 'http://127.0.0.1:8081'
HEADERS = {'Host': 'erpnext.local'}

session = requests.Session()
session.headers.update(HEADERS)
session.post(f'{ERPNEXT_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'KsbioAdmin2026'})

# Test creating a simple account
test_data = {
    "account_name": "Test Account Cash",
    "account_type": "Cash",
    "root_type": "Asset",
    "is_group": 0
}

resp = session.post(f'{ERPNEXT_URL}/api/resource/Account', json=test_data)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:500]}')
