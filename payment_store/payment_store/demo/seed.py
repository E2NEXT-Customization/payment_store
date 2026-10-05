import frappe
from frappe.utils import nowdate, add_days

def execute():
    try:
        create_demo_cashboxes()
        create_demo_rates()
        create_demo_deals()
        frappe.db.commit()
        print("Seed data successfully injected!")
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_demo_cashboxes():
    for name in ["Main Cashbox", "Branch A Cashbox"]:
        if not frappe.db.exists("Cashbox", name):
            frappe.get_doc({
                "doctype": "Cashbox",
                "cashbox_name": name,
                "iqd_account": "Cash - P",
                "usd_account": "Cash - P",
                "is_active": 1
            }).insert(ignore_permissions=True)

def create_demo_rates():
    if not frappe.db.exists("PS Daily Rate", {"date": nowdate()}):
        frappe.get_doc({
            "doctype": "PS Daily Rate",
            "date": nowdate(),
            "currency": "USD",
            "cbi_official_rate": 1310,
            "company_buy_rate": 1500,
            "company_sell_rate": 1520,
            "is_active": 1
        }).insert(ignore_permissions=True)

def create_demo_deals():
    # Will skip for now to avoid complexity during basic seed,
    # but the structure is here for testing.
    pass
