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
                    accounts.append({
                        "account_name": name,
                        "cl_amount": cl_amount,
                        "dr_amount": dr_amount,
                        "cr_amount": cr_amount,
                        "op_amount": op_amount
                    })
    
    return accounts

def create_root_accounts(session):
    """Create root accounts for the chart of accounts"""
    root_accounts = [
        {"account_name": "Bank Accounts", "account_type": "Bank", "root_type": "Asset", "is_group": 1, "company": "KSBio"},
        {"account_name": "Cash Accounts", "account_type": "Cash", "root_type": "Asset", "is_group": 1, "company": "KSBio"},
        {"account_name": "Receivable Accounts", "account_type": "Receivable", "root_type": "Asset", "is_group": 1, "company": "KSBio"},
        {"account_name": "Payable Accounts", "account_type": "Payable", "root_type": "Liability", "is_group": 1, "company": "KSBio"},
        {"account_name": "Sales Accounts", "account_type": "Income", "root_type": "Income", "is_group": 1, "company": "KSBio"},
        {"account_name": "Purchase Accounts", "account_type": "Expense", "root_type": "Expense", "is_group": 1, "company": "KSBio"},
    ]
    
    print("\nCreating root accounts...")
    for acc in root_accounts:
        result = create_account(session, acc)
        if result["success"]:
            print(f"  Created root: {acc['account_name']}")
        else:
            print(f"  Error creating {acc['account_name']}: {result.get('error', '')[:80]}")
        time.sleep(0.3)
    
    return root_accounts

def determine_account_type(account_name, cl_amount, dr_amount, cr_amount):
    """Determine account type based on name and amounts"""
    name_upper = account_name.upper()
    
    # Check for Bank accounts
    if 'BANK' in name_upper:
        return ("Bank", "Asset", "Bank Accounts")
    
    # Check for Cash accounts
    if 'CASH' in name_upper:
        return ("Cash", "Asset", "Cash Accounts")
    
    # Check for Receivables (debtors, customers)
    if any(x in name_upper for x in ['DEBTOR', 'CUSTOMER', 'RECEIVABLE', 'SALES LEDGER']):
        return ("Receivable", "Asset", "Receivable Accounts")
    
    # Check for Payables (creditors, suppliers)
    if any(x in name_upper for x in ['CREDITOR', 'SUPPLIER', 'PAYABLE', 'PURCHASE LEDGER']):
        return ("Payable", "Liability", "Payable Accounts")
    
    # Check for Sales/Revenue
    if any(x in name_upper for x in ['SALES', 'REVENUE', 'INCOME']):
        return ("Income", "Income", "Sales Accounts")
    
    # Check for Purchase/Expense
    if any(x in name_upper for x in ['PURCHASE', 'EXPENSE', 'DIRECT EXPENSE', 'INDIRECT EXPENSE']):
        return ("Expense", "Expense", "Purchase Accounts")
    
    # Check for Duties & Taxes
    if any(x in name_upper for x in ['TAX', 'DUTY', 'GST', 'TDS', 'CST', 'VAT']):
        return ("Tax", "Liability", "Payable Accounts")
    
    # Check for Stock/Inventory
    if any(x in name_upper for x in ['STOCK', 'INVENTORY', 'GOODS']):
        return ("Stock", "Asset", "Receivable Accounts")
    
    # Check for Secured Loans
    if any(x in name_upper for x in ['LOAN', 'BORROWING', 'DEPOSIT']):
        return ("Bank", "Liability", "Payable Accounts")
    
    # Default to Cash
    if abs(cl_amount) > 0 or abs(dr_amount) > 0 or abs(cr_amount) > 0:
        return ("Cash", "Asset", "Cash Accounts")
    else:
        return ("Cash", "Asset", "Cash Accounts")

def import_accounts(session, accounts, batch_size=10):
    """Import accounts into ERPNext"""
    success = 0
    failed = 0
    errors = []
    
    print(f"\nImporting {len(accounts)} accounts...")
    
    for i, account in enumerate(accounts):
        # Determine account type and parent
        acc_type, root_type, parent = determine_account_type(
            account['account_name'],
            account['cl_amount'],
            account['dr_amount'],
            account['cr_amount']
        )
        
        # Add company to make full account name
        full_parent = f"{parent} - KSB" if parent else ""
        
        account_data = {
            "account_name": account['account_name'],
            "account_type": acc_type,
            "root_type": root_type,
            "is_group": 0,
            "company": "KSBio",
            "parent_account": full_parent
        }
        
        result = create_account(session, account_data)
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
    
    # First create root accounts
    create_root_accounts(session)
    
    # Now parse and import the accounts
    trial_balance_file = r"C:\Users\Digvijay Patil\Desktop\Tally 12-4-2026\Reports\Trial Balance\TrialBal Ledger Wise.xml"
    
    print("\nParsing Trial Balance XML...")
    try:
        accounts = parse_trial_balance_xml(trial_balance_file)
        print(f"Found {len(accounts)} accounts")
    except Exception as e:
        print(f"Error parsing: {e}")
        accounts = []
    
    # Import accounts
    acc_success, acc_failed = import_accounts(session, accounts)
    
    print("\n" + "=" * 60)
    print(f"Import Complete! Success: {acc_success}, Failed: {acc_failed}")
    print("=" * 60)
