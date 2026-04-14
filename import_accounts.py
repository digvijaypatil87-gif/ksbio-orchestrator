"""
Import GL Accounts from Trial Balance XML
"""

import requests
import xml.etree.ElementTree as ET
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

def create_account(session, data):
    """Create an account in ERPNext"""
    try:
        resp = session.post(f"{ERPNEXT_URL}/api/resource/Account", json=data)
        if resp.status_code == 200:
            result = json.loads(resp.text)
            return {"success": True, "data": result.get("data", {})}
        else:
            error = json.loads(resp.text)
            return {"success": False, "error": error.get("exception", error.get("message", resp.text[:200]))}
    except Exception as e:
        return {"success": False, "error": str(e)}

def parse_tally_xml_utf16(filepath):
    """Parse Tally XML file (UTF-16 encoded)"""
    with open(filepath, 'r', encoding='utf-16') as f:
        content = f.read()
    if content.startswith('\ufeff'):
        content = content[1:]
    return ET.fromstring(content)

def parse_trial_balance_xml(filepath):
    """Parse Trial Balance XML and extract account data"""
    tree = parse_tally_xml_utf16(filepath)
    
    accounts = []
    
    for acc_name in tree.iter():
        if 'DSPACCNAME' in acc_name.tag:
            name = None
            for child in acc_name.iter():
                if 'DSPDISPNAME' in child.tag and child.text:
                    name = child.text.strip()
                    break
            
            if name and name != 'Opening Stock':
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
                
                if name and name != '1':
                    # Determine account type based on name patterns
                    account_type = "Cash"
                    if any(x in name.upper() for x in ['BANK', 'CASH']):
                        account_type = "Cash"
                    elif any(x in name.upper() for x in ['SALES', 'REVENUE']):
                        account_type = "Income"
                    elif any(x in name.upper() for x in ['PURCHASE', 'EXPENSE']):
                        account_type = "Expense"
                    elif any(x in name.upper() for x in ['DEBTOR', 'CUSTOMER', 'RECEIVABLE']):
                        account_type = "Receivable"
                    elif any(x in name.upper() for x in ['CREDITOR', 'SUPPLIER', 'PAYABLE']):
                        account_type = "Payable"
                    elif any(x in name.upper() for x in ['STOCK', 'INVENTORY']):
                        account_type = "Stock"
                    else:
                        account_type = "Cash"  # Default
                    
                    accounts.append({
                        "account_name": name,
                        "account_type": account_type,
                        "parent_account": "",
                        "root_type": account_type,
                        "is_group": 0
                    })
    
    return accounts

def import_accounts(session, accounts, batch_size=10):
    """Import accounts into ERPNext"""
    success = 0
    failed = 0
    errors = []
    
    print(f"\nImporting {len(accounts)} accounts...")
    
    for i, account in enumerate(accounts):
        result = create_account(session, account)
        if result["success"]:
            success += 1
        else:
            failed += 1
            if len(errors) < 5:
                errors.append(f"  {account['account_name']}: {result.get('error', 'Unknown')[:80]}")
        
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(accounts)} (Success: {success}, Failed: {failed})")
        
        if (i + 1) % batch_size == 0:
            time.sleep(0.3)
    
    print(f"  Final: {success} imported, {failed} failed")
    if errors:
        print("  First few errors:")
        for e in errors[:5]:
            print(f"    {e}")
    
    return success, failed

if __name__ == "__main__":
    print("=" * 60)
    print("GL Account Import from Trial Balance")
    print("=" * 60)
    
    session = login()
    
    trial_balance_file = r"C:\Users\Digvijay Patil\Desktop\Tally 12-4-2026\Reports\Trial Balance\TrialBal Ledger Wise.xml"
    
    print("\nParsing Trial Balance XML...")
    try:
        accounts = parse_trial_balance_xml(trial_balance_file)
        print(f"Found {len(accounts)} accounts")
    except Exception as e:
        print(f"Error parsing: {e}")
        accounts = []
    
    print(f"\nAccount types breakdown:")
    types = {}
    for a in accounts:
        t = a['account_type']
        types[t] = types.get(t, 0) + 1
    for t, c in types.items():
        print(f"  {t}: {c}")
    
    # Import accounts
    acc_success, acc_failed = import_accounts(session, accounts)
    
    print("\n" + "=" * 60)
    print(f"Import Complete! Success: {acc_success}, Failed: {acc_failed}")
    print("=" * 60)
