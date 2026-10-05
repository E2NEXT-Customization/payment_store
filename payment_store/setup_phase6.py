import frappe

def execute():
    try:
        create_denomination_count()
        create_cashbox_reconciliation()
        create_spot_check()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_denomination_count():
    doctype_name = "Denomination Count"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "denomination", "fieldtype": "Currency", "label": "Denomination", "reqd": 1, "in_list_view": 1},
                {"fieldname": "count", "fieldtype": "Int", "label": "Count", "reqd": 1, "in_list_view": 1},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "read_only": 1, "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_cashbox_reconciliation():
    doctype_name = "Cashbox Reconciliation"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "is_submittable": 1,
            "naming_rule": "Expression",
            "autoname": "format:CR-{YYYY}-{MM}-{#####}",
            "fields": [
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "session", "fieldtype": "Link", "options": "Cashbox Session", "label": "Session", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nPending Approval\nApproved\nRejected\nSubmitted", "label": "Status", "default": "Draft"},
                {"fieldname": "denominations_section", "fieldtype": "Section Break", "label": "Denominations"},
                {"fieldname": "denominations", "fieldtype": "Table", "options": "Denomination Count", "label": "Denominations"},
                {"fieldname": "reconciliation_results_section", "fieldtype": "Section Break", "label": "Results"},
                {"fieldname": "results", "fieldtype": "Code", "options": "JSON", "label": "Reconciliation Results", "read_only": 1},
                {"fieldname": "explainer_output", "fieldtype": "Code", "options": "JSON", "label": "Explainer Diagnosis", "read_only": 1},
                {"fieldname": "approval_section", "fieldtype": "Section Break", "label": "Variance Approval", "depends_on": "eval:doc.status=='Pending Approval'"},
                {"fieldname": "variance_reason", "fieldtype": "Small Text", "label": "Variance Reason"},
                {"fieldname": "z_report_hash", "fieldtype": "Data", "label": "Z-Report Hash", "read_only": 1, "hidden": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
                {"role": "Payment Store Cashier", "read": 1, "write": 1, "create": 1, "submit": 1},
                {"role": "Payment Store Auditor", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_spot_check():
    doctype_name = "Spot Check"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "is_submittable": 1,
            "naming_rule": "Expression",
            "autoname": "format:SC-{YYYY}-{MM}-{#####}",
            "fields": [
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "session", "fieldtype": "Link", "options": "Cashbox Session", "label": "Session", "reqd": 1},
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "expected_amount", "fieldtype": "Currency", "label": "Expected Amount", "read_only": 1},
                {"fieldname": "counted_amount", "fieldtype": "Currency", "label": "Counted Amount", "reqd": 1},
                {"fieldname": "variance", "fieldtype": "Currency", "label": "Variance", "read_only": 1},
                {"fieldname": "is_mismatch", "fieldtype": "Check", "label": "Mismatch Detected", "read_only": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
                {"role": "Payment Store Auditor", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")
