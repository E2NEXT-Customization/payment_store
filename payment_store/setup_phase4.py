import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    try:
        create_customer_currency_account_table()
        add_custom_fields_to_customer()
        create_cashbox_transaction()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_customer_currency_account_table():
    doctype_name = "Customer Currency Account"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "receivable_account", "fieldtype": "Link", "options": "Account", "label": "Receivable Account", "reqd": 1, "in_list_view": 1},
                {"fieldname": "payable_account", "fieldtype": "Link", "options": "Account", "label": "Payable Account", "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def add_custom_fields_to_customer():
    custom_fields = {
        "Customer": [
            {
                "fieldname": "ps_currency_accounts",
                "label": "Currency Accounts (Payment Store)",
                "fieldtype": "Table",
                "options": "Customer Currency Account",
                "insert_after": "accounts"
            }
        ]
    }
    create_custom_fields(custom_fields)
    print("Added custom fields to Customer")

def create_cashbox_transaction():
    doctype_name = "Cashbox Transaction"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "is_submittable": 1,
            "naming_rule": "Expression",
            "autoname": "format:PS-TX-.YYYY.-.#####",
            "fields": [
                {"fieldname": "type", "fieldtype": "Select", "label": "Type", "reqd": 1, "options": "Opening\nCash In\nCash Out\nExpense\nCapital Injection\nCustomer Deposit\nCustomer Withdrawal\nCustomer Receipt\nCustomer Payment\nTransfer\nCounterfeit Write-off"},
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "session", "fieldtype": "Link", "options": "Cashbox Session", "label": "Session", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1},
                {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "depends_on": "eval:in_list(['Cash In', 'Capital Injection', 'Customer Deposit'], doc.type)"},
                {"fieldname": "details_section", "fieldtype": "Section Break", "label": "Details"},
                {"fieldname": "party", "fieldtype": "Dynamic Link", "options": "party_type", "label": "Party"},
                {"fieldname": "party_type", "fieldtype": "Link", "options": "DocType", "label": "Party Type"},
                {"fieldname": "destination_cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Destination Cashbox", "depends_on": "eval:doc.type=='Transfer'"},
                {"fieldname": "transfer_status", "fieldtype": "Select", "options": "Pending\nConfirmed\nRejected", "label": "Transfer Status", "depends_on": "eval:doc.type=='Transfer'", "read_only": 1, "default": "Pending"},
                {"fieldname": "incoming_transfer_reference", "fieldtype": "Link", "options": "Cashbox Transaction", "label": "Incoming Transfer Ref", "read_only": 1},
                {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},
                {"fieldname": "system_section", "fieldtype": "Section Break"},
                {"fieldname": "idempotency_key", "fieldtype": "Data", "label": "Idempotency Key", "unique": 1, "read_only": 1},
                {"fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "label": "Journal Entry", "read_only": 1}
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
