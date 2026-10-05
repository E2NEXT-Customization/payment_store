import frappe

def execute():
    try:
        # 1. Delete Unauthorized DocTypes
        doctypes_to_delete = [
            "Client Watchlist", "Rate Override Request", "Spot Check",
            "Cashbox Reconciliation", "Denomination Count", "Cashbox Ledger Entry",
            "Cashbox Session", "Customer Currency Account", "Exchange Rate Board",
            "Cashbox Account"
        ]
        
        for dt in doctypes_to_delete:
            if frappe.db.exists("DocType", dt):
                frappe.delete_doc("DocType", dt, ignore_missing=True, force=True)
                print(f"Deleted DocType: {dt}")

        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e
