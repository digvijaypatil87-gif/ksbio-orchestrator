import requests
import xml.etree.ElementTree as ET
import json

# ERPNext API configuration
ERPNEXT_URL = "http://127.0.0.1:8081"
API_KEY = "a468a816b7a3e14"
API_SECRET = "3877e9ef90241a0"

# Login and get session
session = requests.Session()
session.headers.update({"Host": "erpnext.local"})

# Login
login_resp = session.post(
    f"{ERPNEXT_URL}/api/method/login",
    data={"usr": "Administrator", "pwd": "KsbioAdmin2026"}
)
print(f"Login: {login_resp.status_code}")
login_data = login_resp.json()
print(json.dumps(login_data, indent=2))

# Test API access with session cookie
me_resp = session.get(f"{ERPNEXT_URL}/api/resource/User")
print(f"\nUser API: {me_resp.status_code}")
print(me_resp.text[:500])
