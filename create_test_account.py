import frappe
doc = frappe.new_doc("Account")
doc.account_name = "Test Bench Account"
doc.account_type = "Cash"
doc.root_type = "Asset"
doc.is_group = 0
doc.insert()
frappe.db.commit()
print(f"Created: {doc.name}")
