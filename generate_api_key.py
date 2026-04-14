import frappe
import os

os.chdir('/home/frappe/frappe-bench/sites')
frappe.init(site='erpnext.local')
frappe.connect()

# Generate API key and secret
api_key = frappe.generate_hash(length=15)
api_secret = frappe.generate_hash(length=15)

# Update the api_key in the user table directly (not encrypted)
frappe.db.sql("UPDATE tabUser SET api_key=%s WHERE name='Administrator'", (api_key,))

# Use set_encrypted_password to store the api_secret
from frappe.utils.password import set_encrypted_password
set_encrypted_password('User', 'Administrator', api_secret, 'api_secret')

frappe.db.commit()

print(f"API Key: {api_key}")
print(f"API Secret: {api_secret}")
