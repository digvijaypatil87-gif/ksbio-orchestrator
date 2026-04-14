import frappe
import sys
import os

# Set the site path explicitly
os.chdir('/home/frappe/frappe-bench/sites')

frappe.init(site='erpnext.local')
frappe.connect()
user = frappe.get_doc('User', 'Administrator')
user.password = 'KsbioAdmin2026'
user.save()
print('Password updated for Administrator')
frappe.db.commit()
