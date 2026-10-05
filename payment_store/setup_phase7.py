import frappe

def execute():
    try:
        create_reports()
        create_dashboard_components()
        frappe.db.commit()
        print("Phase 7 Reports & Dashboards Created")
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_reports():
    reports = [
        {"name": "Client Statement", "ref_doctype": "Exchange Deal"},
        {"name": "Daily Trading", "ref_doctype": "Exchange Deal"},
        {"name": "Variance Patterns", "ref_doctype": "Cashbox Closing"}
    ]
    
    for r in reports:
        if not frappe.db.exists("Report", r["name"]):
            frappe.get_doc({
                "doctype": "Report",
                "name": r["name"],
                "report_name": r["name"],
                "ref_doctype": r["ref_doctype"],
                "report_type": "Script Report",
                "is_standard": "Yes",
                "module": "Payment Store"
            }).insert(ignore_permissions=True)
            print(f"Created Report {r['name']}")

def create_dashboard_components():
    # Number Cards
    cards = [
        {"name": "USD Cash", "document_type": "Exchange Deal", "function": "Sum", "aggregate_function_based_on": "usd_amount"},
        {"name": "IQD Cash", "document_type": "Exchange Deal", "function": "Sum", "aggregate_function_based_on": "iqd_amount"}
    ]
    
    for c in cards:
        if not frappe.db.exists("Number Card", c["name"]):
            frappe.get_doc({
                "doctype": "Number Card",
                "name": c["name"],
                "label": c["name"],
                "document_type": c["document_type"],
                "function": c["function"],
                "aggregate_function_based_on": c["aggregate_function_based_on"],
                "is_standard": 1,
                "module": "Payment Store"
            }).insert(ignore_permissions=True)
            print(f"Created Number Card {c['name']}")
