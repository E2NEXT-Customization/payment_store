import frappe

def execute():
    try:
        create_exchange_rate_board()
        create_cashbox_child_tables()
        create_cashbox()
        create_cashbox_session()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_exchange_rate_board():
    doctype_name = "Exchange Rate Board"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "naming_rule": "Expression",
            "autoname": "format:ERB-{currency}-{effective_from}",
            "fields": [
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today"},
                {"fieldname": "effective_from", "fieldtype": "Datetime", "label": "Effective From", "reqd": 1, "default": "Now"},
                {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "cbi_official_rate", "fieldtype": "Currency", "label": "CBI Official Rate", "reqd": 1},
                {"fieldname": "company_buy_rate", "fieldtype": "Currency", "label": "Company Buy Rate", "reqd": 1},
                {"fieldname": "company_sell_rate", "fieldtype": "Currency", "label": "Company Sell Rate", "reqd": 1},
                {"fieldname": "section_break_1", "fieldtype": "Section Break"},
                {"fieldname": "set_by", "fieldtype": "Link", "options": "User", "label": "Set By", "default": "frappe.session.user", "read_only": 1},
                {"fieldname": "approved_by", "fieldtype": "Link", "options": "User", "label": "Approved By"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Cashier", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_cashbox_child_tables():
    if not frappe.db.exists("DocType", "Cashbox Account"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Cashbox Account",
            "module": "Payment Store",
            "custom": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "account", "fieldtype": "Link", "options": "Account", "label": "Account", "reqd": 1, "in_list_view": 1},
                {"fieldname": "max_cash_limit", "fieldtype": "Currency", "label": "Max Cash Limit", "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created DocType: Cashbox Account")

    if not frappe.db.exists("DocType", "Cashbox User"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Cashbox User",
            "module": "Payment Store",
            "custom": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "user", "fieldtype": "Link", "options": "User", "label": "User", "reqd": 1, "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created DocType: Cashbox User")

def create_cashbox():
    doctype_name = "Cashbox"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "naming_rule": "By fieldname",
            "autoname": "field:cashbox_name",
            "fields": [
                {"fieldname": "cashbox_name", "fieldtype": "Data", "label": "Cashbox Name", "reqd": 1, "unique": 1},
                {"fieldname": "branch", "fieldtype": "Link", "options": "Branch", "label": "Branch"},
                {"fieldname": "type", "fieldtype": "Select", "label": "Type", "options": "Main\nCashier\nVault", "reqd": 1},
                {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "iqd_account", "fieldtype": "Link", "options": "Account", "label": "IQD Account", "reqd": 1},
                {"fieldname": "accounts_section", "fieldtype": "Section Break", "label": "Foreign Currency Accounts"},
                {"fieldname": "accounts", "fieldtype": "Table", "options": "Cashbox Account", "label": "Accounts"},
                {"fieldname": "users_section", "fieldtype": "Section Break", "label": "Assigned Users"},
                {"fieldname": "users", "fieldtype": "Table", "options": "Cashbox User", "label": "Users"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Cashier", "read": 1},
                {"role": "Payment Store Auditor", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_cashbox_session():
    doctype_name = "Cashbox Session"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "naming_rule": "Expression",
            "autoname": "format:CS-{cashbox}-{YYYY}-{MM}-{#####}",
            "fields": [
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "cashier", "fieldtype": "Link", "options": "User", "label": "Cashier", "reqd": 1, "default": "frappe.session.user"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nCounting\nPending Review\nClosed\nLocked", "default": "Open"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "opened_at", "fieldtype": "Datetime", "label": "Opened At", "reqd": 1, "default": "Now"},
                {"fieldname": "closed_at", "fieldtype": "Datetime", "label": "Closed At", "read_only": 1},
                {"fieldname": "opening_balances", "fieldtype": "Code", "options": "JSON", "label": "Opening Balances", "read_only": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Cashier", "read": 1, "write": 1, "create": 1},
                {"role": "Payment Store Auditor", "read": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")
