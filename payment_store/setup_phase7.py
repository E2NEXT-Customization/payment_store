import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    try:
        create_client_watchlist()
        create_override_request()
        update_settings()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_client_watchlist():
    doctype_name = "Client Watchlist"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "autoname": "field:client_name",
            "fields": [
                {"fieldname": "client_name", "fieldtype": "Data", "label": "Client Name Pattern", "reqd": 1, "unique": 1},
                {"fieldname": "id_pattern", "fieldtype": "Data", "label": "ID Pattern"},
                {"fieldname": "phone_pattern", "fieldtype": "Data", "label": "Phone Pattern"},
                {"fieldname": "action", "fieldtype": "Select", "options": "Block\nRequire Approval\nWarn", "label": "Action", "reqd": 1},
                {"fieldname": "reason", "fieldtype": "Small Text", "label": "Reason"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Auditor", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_override_request():
    doctype_name = "Rate Override Request"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "is_submittable": 1,
            "naming_rule": "Expression",
            "autoname": "format:ROR-{YYYY}-{MM}-{#####}",
            "fields": [
                {"fieldname": "exchange_deal", "fieldtype": "Link", "options": "Exchange Deal", "label": "Exchange Deal", "reqd": 1},
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox"},
                {"fieldname": "cashier", "fieldtype": "Link", "options": "User", "label": "Cashier"},
                {"fieldname": "requested_rate", "fieldtype": "Currency", "label": "Requested Rate", "reqd": 1},
                {"fieldname": "reason", "fieldtype": "Small Text", "label": "Reason", "reqd": 1},
                {"fieldname": "status", "fieldtype": "Select", "options": "Pending\nApproved\nRejected", "label": "Status", "default": "Pending"},
                {"fieldname": "manager", "fieldtype": "Link", "options": "User", "label": "Manager"},
                {"fieldname": "decision_reason", "fieldtype": "Small Text", "label": "Decision Reason"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
                {"role": "Payment Store Cashier", "read": 1, "write": 1, "create": 1, "submit": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def update_settings():
    custom_fields = {
        "Payment Store Settings": [
            {"fieldname": "compliance_section", "fieldtype": "Section Break", "label": "Compliance Thresholds"},
            {"fieldname": "traveler_limit_usd", "fieldtype": "Currency", "label": "Traveler Limit (USD/Year)"},
            {"fieldname": "structuring_threshold_usd", "fieldtype": "Currency", "label": "Structuring Threshold (USD)"},
            {"fieldname": "structuring_window_days", "fieldtype": "Int", "label": "Structuring Window (Days)"},
            {"fieldname": "block_backdating", "fieldtype": "Check", "label": "Block Backdating"},
            {"fieldname": "notifications_section", "fieldtype": "Section Break", "label": "Notifications"},
            {"fieldname": "manager_webhook", "fieldtype": "Data", "label": "Manager Webhook (Optional)"}
        ]
    }
    create_custom_fields(custom_fields)
    print("Updated Payment Store Settings with Compliance fields")
