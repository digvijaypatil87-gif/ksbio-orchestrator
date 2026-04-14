"""
Setup ERPNext with required reference data before importing Tally data
"""

import requests
import json
import time

ERPNEXT_URL = "http://127.0.0.1:8081"
HEADERS = {"Host": "erpnext.local"}

def login():
    session = requests.Session()
    session.headers.update(HEADERS)
    resp = session.post(
        f"{ERPNEXT_URL}/api/method/login",
        data={"usr": "Administrator", "pwd": "KsbioAdmin2026"}
    )
    print(f"Login: {resp.status_code}")
    return session

def create_record(session, doctype, data):
    """Create a record"""
    resp = session.post(f"{ERPNEXT_URL}/api/resource/{doctype}", json=data)
    if resp.status_code == 200:
        result = json.loads(resp.text)
        name = result.get("data", {}).get("name", "Created")
        return {"success": True, "name": name}
    else:
        error = json.loads(resp.text)
        msg = error.get("exception", error.get("message", resp.text[:200]))
        return {"success": False, "error": msg}

def setup_uom(session):
    """Create UOM"""
    print("\n=== Creating UOM: Nos ===")
    result = create_record(session, "UOM", {
        "uom_name": "Nos",
        "must_be_whole_number": 1
    })
    if result["success"]:
        print(f"  Success: {result['name']}")
    else:
        print(f"  Error: {result.get('error')}")
    return result["success"]

def setup_item_groups(session):
    """Create Item Groups"""
    print("\n=== Creating Item Groups ===")
    
    groups = [
        {"name": "All Item Groups", "parent_item_group": ""},
        {"name": "Products", "parent_item_group": "All Item Groups"},
        {"name": "Raw Materials", "parent_item_group": "All Item Groups"},
        {"name": "Services", "parent_item_group": "All Item Groups"},
    ]
    
    success = 0
    for g in groups:
        result = create_record(session, "Item Group", {
            "item_group_name": g["name"],
            "parent_item_group": g["parent_item_group"],
            "is_group": 0 if g["name"] != "All Item Groups" else 0
        })
        if result["success"]:
            success += 1
            print(f"  Created: {g['name']}")
        else:
            print(f"  Error creating {g['name']}: {result.get('error')[:100]}")
        time.sleep(0.2)
    
    return success

def setup_customer_groups(session):
    """Create Customer Groups"""
    print("\n=== Creating Customer Groups ===")
    
    groups = [
        {"name": "All Customer Groups", "parent_customer_group": ""},
        {"name": "Commercial - Sold to Customer", "parent_customer_group": "All Customer Groups"},
        {"name": "Individual", "parent_customer_group": "All Customer Groups"},
        {"name": "Retail", "parent_customer_group": "All Customer Groups"},
    ]
    
    success = 0
    for g in groups:
        result = create_record(session, "Customer Group", {
            "customer_group_name": g["name"],
            "parent_customer_group": g["parent_customer_group"]
        })
        if result["success"]:
            success += 1
            print(f"  Created: {g['name']}")
        else:
            print(f"  Error creating {g['name']}: {result.get('error')[:100]}")
        time.sleep(0.2)
    
    return success

def setup_supplier_groups(session):
    """Create Supplier Groups"""
    print("\n=== Creating Supplier Groups ===")
    
    groups = [
        {"name": "All Supplier Groups", "parent_supplier_group": ""},
        {"name": "Services - Raw Material Supplier", "parent_supplier_group": "All Supplier Groups"},
        {"name": "Product Supplier", "parent_supplier_group": "All Supplier Groups"},
    ]
    
    success = 0
    for g in groups:
        result = create_record(session, "Supplier Group", {
            "supplier_group_name": g["name"],
            "parent_supplier_group": g["parent_supplier_group"]
        })
        if result["success"]:
            success += 1
            print(f"  Created: {g['name']}")
        else:
            print(f"  Error creating {g['name']}: {result.get('error')[:100]}")
        time.sleep(0.2)
    
    return success

def setup_territories(session):
    """Create Territories"""
    print("\n=== Creating Territories ===")
    
    territories = [
        {"name": "All Territories", "parent_territory": ""},
        {"name": "India", "parent_territory": "All Territories"},
    ]
    
    success = 0
    for t in territories:
        result = create_record(session, "Territory", {
            "territory_name": t["name"],
            "parent_territory": t["parent_territory"]
        })
        if result["success"]:
            success += 1
            print(f"  Created: {t['name']}")
        else:
            print(f"  Error creating {t['name']}: {result.get('error')[:100]}")
        time.sleep(0.2)
    
    return success

if __name__ == "__main__":
    print("=" * 60)
    print("ERPNext Setup Script")
    print("=" * 60)
    
    session = login()
    
    # Setup UOM
    uom_success = setup_uom(session)
    
    # Setup Item Groups
    item_group_success = setup_item_groups(session)
    
    # Setup Customer Groups
    cust_group_success = setup_customer_groups(session)
    
    # Setup Supplier Groups
    supp_group_success = setup_supplier_groups(session)
    
    # Setup Territories
    terr_success = setup_territories(session)
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print(f"  UOMs: {'OK' if uom_success else 'Failed'}")
    print(f"  Item Groups: {item_group_success} created")
    print(f"  Customer Groups: {cust_group_success} created")
    print(f"  Supplier Groups: {supp_group_success} created")
    print(f"  Territories: {terr_success} created")
    print("=" * 60)
