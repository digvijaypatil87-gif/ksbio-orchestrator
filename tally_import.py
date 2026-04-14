"""
Tally to ERPNext Import Script
Parses Tally XML exports and imports into ERPNext via REST API
"""

import requests
import xml.etree.ElementTree as ET
import json
import time

# ERPNext API configuration
ERPNEXT_URL = "http://127.0.0.1:8081"
HEADERS = {"Host": "erpnext.local"}

def login():
    """Login to ERPNext and return session"""
    session = requests.Session()
    session.headers.update(HEADERS)
    resp = session.post(
        f"{ERPNEXT_URL}/api/method/login",
        data={"usr": "Administrator", "pwd": "KsbioAdmin2026"}
    )
    if resp.status_code != 200:
        raise Exception(f"Login failed: {resp.text}")
    print("Logged in successfully")
    return session

def create_record(session, doctype, data):
    """Create a record in ERPNext"""
    try:
        resp = session.post(
            f"{ERPNEXT_URL}/api/resource/{doctype}",
            json=data
        )
        if resp.status_code == 200:
            result = json.loads(resp.text)
            return {"success": True, "data": result.get("data", {})}
        else:
            error = json.loads(resp.text)
            return {"success": False, "error": error.get("exception", error.get("message", resp.text[:200]))}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_customer(session, customer_data):
    """Create a customer in ERPNext"""
    return create_record(session, "Customer", customer_data)

def create_supplier(session, supplier_data):
    """Create a supplier in ERPNext"""
    return create_record(session, "Supplier", supplier_data)

def create_item(session, item_data):
    """Create an item in ERPNext"""
    return create_record(session, "Item", item_data)

def parse_tally_xml_utf16(filepath):
    """Parse Tally XML file (UTF-16 encoded)"""
    with open(filepath, 'r', encoding='utf-16') as f:
        content = f.read()
    if content.startswith('\ufeff'):
        content = content[1:]
    return ET.fromstring(content)

def parse_debtors_xml(filepath):
    """Parse Sundry Debtors XML and extract customer data"""
    tree = parse_tally_xml_utf16(filepath)
    
    customers = []
    
    for acc_name in tree.iter():
        if 'DSPACCNAME' in acc_name.tag:
            name = None
            for child in acc_name.iter():
                if 'DSPDISPNAME' in child.tag and child.text:
                    name = child.text.strip()
                    break
            
            if name and name != 'Opening Stock' and name != '1':
                cl_amount = 0
                dr_amount = 0
                cr_amount = 0
                op_amount = 0
                
                parent = tree
                children = list(parent)
                for i, child in enumerate(children):
                    if child is acc_name and i + 1 < len(children):
                        next_elem = children[i + 1]
                        if 'DSPACCINFO' in next_elem.tag:
                            for elem in next_elem.iter():
                                if 'DSPCLAMTA' in elem.tag and elem.text:
                                    try:
                                        cl_amount = float(elem.text.strip())
                                    except:
                                        pass
                                elif 'DSPDRAMTA' in elem.tag and elem.text:
                                    try:
                                        dr_amount = float(elem.text.strip())
                                    except:
                                        pass
                                elif 'DSPCRAMTA' in elem.tag and elem.text:
                                    try:
                                        cr_amount = float(elem.text.strip())
                                    except:
                                        pass
                                elif 'DSPOPAMTA' in elem.tag and elem.text:
                                    try:
                                        op_amount = float(elem.text.strip())
                                    except:
                                        pass
                            break
                
                if name:
                    customers.append({
                        "customer_name": name,
                        "customer_type": "Individual",
                        "customer_group": "Commercial - Sold to Customer",
                        "territory": "India",
                        "opening_balance": abs(cl_amount) if cl_amount < 0 else 0,
                        "credit_limit": 1000000
                    })
    
    return customers

def parse_creditors_xml(filepath):
    """Parse Sundry Creditors XML and extract supplier data"""
    tree = parse_tally_xml_utf16(filepath)
    
    suppliers = []
    
    for acc_name in tree.iter():
        if 'DSPACCNAME' in acc_name.tag:
            name = None
            for child in acc_name.iter():
                if 'DSPDISPNAME' in child.tag and child.text:
                    name = child.text.strip()
                    break
            
            if name and name != 'Opening Stock' and name != '1':
                cl_amount = 0
                dr_amount = 0
                cr_amount = 0
                op_amount = 0
                
                parent = tree
                children = list(parent)
                for i, child in enumerate(children):
                    if child is acc_name and i + 1 < len(children):
                        next_elem = children[i + 1]
                        if 'DSPACCINFO' in next_elem.tag:
                            for elem in next_elem.iter():
                                if 'DSPCLAMTA' in elem.tag and elem.text:
                                    try:
                                        cl_amount = float(elem.text.strip())
                                    except:
                                        pass
                                elif 'DSPDRAMTA' in elem.tag and elem.text:
                                    try:
                                        dr_amount = float(elem.text.strip())
                                    except:
                                        pass
                                elif 'DSPCRAMTA' in elem.tag and elem.text:
                                    try:
                                        cr_amount = float(elem.text.strip())
                                    except:
                                        pass
                                elif 'DSPOPAMTA' in elem.tag and elem.text:
                                    try:
                                        op_amount = float(elem.text.strip())
                                    except:
                                        pass
                            break
                
                if name:
                    suppliers.append({
                        "supplier_name": name,
                        "supplier_group": "Services - Raw Material Supplier",
                        "territory": "India",
                        "opening_balance": abs(cl_amount) if cl_amount > 0 else 0
                    })
    
    return suppliers

def parse_stock_xml(filepath):
    """Parse Stock Summary XML and extract item data"""
    tree = parse_tally_xml_utf16(filepath)
    
    items = []
    
    for acc_name in tree.iter():
        if 'DSPACCNAME' in acc_name.tag:
            name = None
            for child in acc_name.iter():
                if 'DSPDISPNAME' in child.tag and child.text:
                    name = child.text.strip()
                    break
            
            if name and name != 'Opening Stock' and name != '1':
                cl_amount = 0
                
                parent = tree
                children = list(parent)
                for i, child in enumerate(children):
                    if child is acc_name and i + 1 < len(children):
                        next_elem = children[i + 1]
                        if 'DSPACCINFO' in next_elem.tag:
                            for elem in next_elem.iter():
                                if 'DSPCLAMTA' in elem.tag and elem.text:
                                    try:
                                        cl_amount = float(elem.text.strip())
                                    except:
                                        pass
                            break
                
                if name:
                    item_code = name.replace(" ", "_").replace("/", "-").replace("&", "AND")[:140]
                    items.append({
                        "item_code": item_code,
                        "item_name": name,
                        "item_group": "All Item Groups",
                        "stock_uom": "Nos",
                        "is_stock_item": 1
                    })
    
    return items

def import_customers(session, customers, batch_size=10):
    """Import customers into ERPNext"""
    success = 0
    failed = 0
    errors = []
    
    print(f"\nImporting {len(customers)} customers...")
    
    for i, customer in enumerate(customers):
        result = create_customer(session, customer)
        if result["success"]:
            success += 1
        else:
            failed += 1
            if len(errors) < 5:
                errors.append(f"  {customer['customer_name']}: {result.get('error', 'Unknown')}")
        
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(customers)} (Success: {success}, Failed: {failed})")
        
        # Small delay to avoid overwhelming the API
        if (i + 1) % batch_size == 0:
            time.sleep(0.5)
    
    print(f"  Final: {success} imported, {failed} failed")
    if errors:
        print("  First few errors:")
        for e in errors[:5]:
            print(f"    {e}")
    
    return success, failed

def import_suppliers(session, suppliers, batch_size=10):
    """Import suppliers into ERPNext"""
    success = 0
    failed = 0
    errors = []
    
    print(f"\nImporting {len(suppliers)} suppliers...")
    
    for i, supplier in enumerate(suppliers):
        result = create_supplier(session, supplier)
        if result["success"]:
            success += 1
        else:
            failed += 1
            if len(errors) < 5:
                errors.append(f"  {supplier['supplier_name']}: {result.get('error', 'Unknown')}")
        
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(suppliers)} (Success: {success}, Failed: {failed})")
        
        if (i + 1) % batch_size == 0:
            time.sleep(0.5)
    
    print(f"  Final: {success} imported, {failed} failed")
    if errors:
        print("  First few errors:")
        for e in errors[:5]:
            print(f"    {e}")
    
    return success, failed

def import_items(session, items, batch_size=10):
    """Import items into ERPNext"""
    success = 0
    failed = 0
    errors = []
    
    print(f"\nImporting {len(items)} items...")
    
    for i, item in enumerate(items):
        result = create_item(session, item)
        if result["success"]:
            success += 1
        else:
            failed += 1
            if len(errors) < 5:
                errors.append(f"  {item['item_name']}: {result.get('error', 'Unknown')}")
        
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(items)} (Success: {success}, Failed: {failed})")
        
        if (i + 1) % batch_size == 0:
            time.sleep(0.5)
    
    print(f"  Final: {success} imported, {failed} failed")
    if errors:
        print("  First few errors:")
        for e in errors[:5]:
            print(f"    {e}")
    
    return success, failed

if __name__ == "__main__":
    print("=" * 60)
    print("Tally to ERPNext Import Script")
    print("=" * 60)
    
    session = login()
    
    debtors_file = r"C:\Users\Digvijay Patil\Desktop\Tally 12-4-2026\Reports\Debtors\Sundry Debtors Ledger Wise.xml"
    creditors_file = r"C:\Users\Digvijay Patil\Desktop\Tally 12-4-2026\Reports\Creditors\Sundry Creditors .xml"
    stock_file = r"C:\Users\Digvijay Patil\Desktop\Tally 12-4-2026\Reports\Stock Summary\StkSum item wise.xml"
    
    print("\nParsing Debtors XML...")
    try:
        customers = parse_debtors_xml(debtors_file)
        print(f"Found {len(customers)} customers")
    except Exception as e:
        print(f"Error parsing debtors: {e}")
        customers = []
    
    print("\nParsing Creditors XML...")
    try:
        suppliers = parse_creditors_xml(creditors_file)
        print(f"Found {len(suppliers)} suppliers")
    except Exception as e:
        print(f"Error parsing creditors: {e}")
        suppliers = []
    
    print("\nParsing Stock Summary XML...")
    try:
        items = parse_stock_xml(stock_file)
        print(f"Found {len(items)} items")
    except Exception as e:
        print(f"Error parsing stock: {e}")
        items = []
    
    print("\n" + "=" * 60)
    print("Starting Import...")
    print("=" * 60)
    
    # Import customers
    cust_success, cust_failed = import_customers(session, customers)
    
    # Import suppliers
    supp_success, supp_failed = import_suppliers(session, suppliers)
    
    # Import items
    item_success, item_failed = import_items(session, items)
    
    print("\n" + "=" * 60)
    print("Import Complete!")
    print(f"  Customers: {cust_success} success, {cust_failed} failed")
    print(f"  Suppliers: {supp_success} success, {supp_failed} failed")
    print(f"  Items: {item_success} success, {item_failed} failed")
    print("=" * 60)
