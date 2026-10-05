import frappe
import os

def execute():
    try:
        create_pages()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_pages():
    pages = [
        {"name": "ps-official-sale", "title": "بيع دولار – سعر رسمي", "module": "Payment Store"},
        {"name": "ps-custom-sale", "title": "بيع دولار – سعر خاص", "module": "Payment Store"},
        {"name": "ps-buy-desk", "title": "شراء دولار", "module": "Payment Store"},
        {"name": "ps-cash-desk", "title": "القاصة", "module": "Payment Store"},
        {"name": "ps-closing-desk", "title": "الجرد والإغلاق", "module": "Payment Store"},
        {"name": "ps-control-tower", "title": "برج المراقبة", "module": "Payment Store"}
    ]

    for p in pages:
        if not frappe.db.exists("Page", p["name"]):
            doc = frappe.get_doc({
                "doctype": "Page",
                "name": p["name"],
                "page_name": p["name"],
                "title": p["title"],
                "module": p["module"],
                "standard": "Yes",
                "roles": [{"role": "Payment Store Manager"}, {"role": "Payment Store Cashier"}]
            })
            doc.insert(ignore_permissions=True)
            print(f"Created Page: {p['name']}")
