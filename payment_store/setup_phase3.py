import frappe

def execute():
    try:
        create_ledger_entry()
        create_exchange_deal()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_ledger_entry():
    doctype_name = "Cashbox Ledger Entry"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "autoname": "autoincrement",
            "fields": [
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "session", "fieldtype": "Link", "options": "Cashbox Session", "label": "Session", "reqd": 1},
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1},
                {"fieldname": "posting_datetime", "fieldtype": "Datetime", "label": "Posting Datetime", "reqd": 1},
                {"fieldname": "voucher_type", "fieldtype": "Link", "options": "DocType", "label": "Voucher Type", "reqd": 1},
                {"fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "label": "Voucher No", "reqd": 1},
                {"fieldname": "direction", "fieldtype": "Select", "options": "In\nOut", "label": "Direction", "reqd": 1},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1},
                {"fieldname": "running_balance", "fieldtype": "Currency", "label": "Running Balance", "reqd": 1},
                {"fieldname": "party", "fieldtype": "Link", "options": "Customer", "label": "Party"},
                {"fieldname": "prev_hash", "fieldtype": "Data", "label": "Previous Hash", "read_only": 1},
                {"fieldname": "entry_hash", "fieldtype": "Data", "label": "Entry Hash", "read_only": 1},
                {"fieldname": "idempotency_key", "fieldtype": "Data", "label": "Idempotency Key", "unique": 1, "read_only": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1},
                {"role": "Payment Store Manager", "read": 1},
                {"role": "Payment Store Auditor", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_exchange_deal():
    doctype_name = "Exchange Deal"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "is_submittable": 1,
            "naming_rule": "Expression",
            "autoname": "format:PS-DL-.YYYY.-.#####",
            "fields": [
                {"fieldname": "deal_type", "fieldtype": "Select", "options": "Sell FC\nBuy FC", "label": "Deal Type", "reqd": 1},
                {"fieldname": "deal_mode", "fieldtype": "Select", "options": "Official\nCustom", "label": "Deal Mode", "reqd": 1},
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "default": "USD"},
                {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "reqd": 1},
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "session", "fieldtype": "Link", "options": "Cashbox Session", "label": "Session", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "reqd": 1},
                {"fieldname": "rate_source", "fieldtype": "Select", "options": "Board\nManual", "label": "Rate Source", "reqd": 1},
                {"fieldname": "foreign_amount", "fieldtype": "Currency", "label": "Foreign Amount", "reqd": 1},
                {"fieldname": "iqd_amount", "fieldtype": "Currency", "label": "IQD Amount", "reqd": 1},
                {"fieldname": "last_edited_field", "fieldtype": "Select", "options": "foreign_amount\niqd_amount", "label": "Last Edited Field", "default": "foreign_amount"},
                {"fieldname": "payment_section", "fieldtype": "Section Break"},
                {"fieldname": "payment_mode", "fieldtype": "Select", "options": "Cash\nOn account\nPartial", "label": "Payment Mode", "default": "Cash"},
                {"fieldname": "paid_amount", "fieldtype": "Currency", "label": "Paid Amount"},
                {"fieldname": "rounding_diff", "fieldtype": "Currency", "label": "Rounding Diff", "read_only": 1},
                {"fieldname": "accounting_section", "fieldtype": "Section Break", "label": "Accounting"},
                {"fieldname": "cost_rate", "fieldtype": "Currency", "label": "Cost Rate (WAC)", "read_only": 1},
                {"fieldname": "profit_iqd", "fieldtype": "Currency", "label": "Profit (IQD)", "read_only": 1},
                {"fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "label": "Journal Entry", "read_only": 1},
                {"fieldname": "wac_snapshot_before", "fieldtype": "Currency", "label": "WAC Before", "read_only": 1},
                {"fieldname": "wac_snapshot_after", "fieldtype": "Currency", "label": "WAC After", "read_only": 1},
                {"fieldname": "compliance_section", "fieldtype": "Section Break", "label": "Compliance"},
                {"fieldname": "notes_verified", "fieldtype": "Check", "label": "Notes Verified"},
                {"fieldname": "approval_status", "fieldtype": "Select", "options": "Not required\nPending\nApproved\nRejected", "label": "Approval Status", "default": "Not required"},
                {"fieldname": "compliance_flags", "fieldtype": "Code", "options": "JSON", "label": "Compliance Flags", "read_only": 1},
                {"fieldname": "system_section", "fieldtype": "Section Break"},
                {"fieldname": "quote_id", "fieldtype": "Data", "label": "Quote ID", "read_only": 1},
                {"fieldname": "idempotency_key", "fieldtype": "Data", "label": "Idempotency Key", "unique": 1, "read_only": 1}
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
