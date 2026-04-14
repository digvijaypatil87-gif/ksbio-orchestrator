import frappe
import getpass

frappe.init('erpnext.local')
frappe.connect()
frappe.utils.password.update_password('Administrator', 'KsbioAdmin2026')
print('Password updated successfully')
