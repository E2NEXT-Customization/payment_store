import frappe

def execute():
    try:
        clean_custom_fields()
        create_child_tables()
        create_ps_daily_rate()
        update_ps_settings()
        update_cashbox()
        update_exchange_deal()
        update_cashbox_transaction()
        create_cashbox_closing()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e

def clean_custom_fields():
    if frappe.db.exists("Custom Field", "Customer-ps_currency_accounts"):
        frappe.delete_doc("Custom Field", "Customer-ps_currency_accounts")
    print("Cleaned Customer custom field")

def create_child_tables():
    # PS Currency Row
    dt = "PS Currency Row"
    if not frappe.db.exists("DocType", dt):
        frappe.get_doc({
            "doctype": "DocType", "name": dt, "module": "Payment Store", "custom": 0, "istable": 1,
            "fields": [
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "precision", "fieldtype": "Int", "label": "Precision", "default": "2"},
                {"fieldname": "cash_account", "fieldtype": "Link", "options": "Account", "label": "Cash Account", "reqd": 1},
                {"fieldname": "running_quantity", "fieldtype": "Currency", "label": "Running Quantity", "read_only": 1, "in_list_view": 1},
                {"fieldname": "wac", "fieldtype": "Currency", "label": "WAC", "read_only": 1, "in_list_view": 1}
            ]
        }).insert(ignore_permissions=True)
        print(f"Created {dt}")

    # Closing Count Row
    dt = "Closing Count Row"
    if not frappe.db.exists("DocType", dt):
        frappe.get_doc({
            "doctype": "DocType", "name": dt, "module": "Payment Store", "custom": 0, "istable": 1,
            "fields": [
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "denomination", "fieldtype": "Currency", "label": "Denomination", "reqd": 1, "in_list_view": 1},
                {"fieldname": "qty", "fieldtype": "Int", "label": "Qty", "reqd": 1, "in_list_view": 1}
            ]
        }).insert(ignore_permissions=True)
        print(f"Created {dt}")

def create_ps_daily_rate():
    dt = "PS Daily Rate"
    if not frappe.db.exists("DocType", dt):
        frappe.get_doc({
            "doctype": "DocType", "name": dt, "module": "Payment Store", "custom": 0,
            "autoname": "format:RATE-{YYYY}-{MM}-{DD}-{currency}",
            "fields": [
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today", "in_list_view": 1},
                {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "default": "USD", "in_list_view": 1},
                {"fieldname": "cbi_official_rate", "fieldtype": "Currency", "label": "CBI Official Rate", "reqd": 1, "in_list_view": 1},
                {"fieldname": "company_buy_rate", "fieldtype": "Currency", "label": "Company Buy Rate", "reqd": 1, "in_list_view": 1},
                {"fieldname": "company_sell_rate", "fieldtype": "Currency", "label": "Company Sell Rate", "reqd": 1, "in_list_view": 1},
                {"fieldname": "set_by", "fieldtype": "Link", "options": "User", "label": "Set By", "read_only": 1, "default": "Administrator"},
                {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1", "in_list_view": 1}
            ],
            "permissions": [{"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1}, {"role": "Payment Store Cashier", "read": 1}]
        }).insert(ignore_permissions=True)
        print(f"Created {dt}")

def update_ps_settings():
    doc = frappe.get_doc("DocType", "Payment Store Settings")
    doc.fields = []
    doc.extend("fields", [
        {"fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Company", "reqd": 1},
        {"fieldname": "currencies", "fieldtype": "Table", "options": "PS Currency Row", "label": "Currencies"},
        {"fieldname": "iqd_rounding_step", "fieldtype": "Int", "label": "IQD Rounding Step", "default": "250"},
        
        {"fieldname": "accounts_section", "fieldtype": "Section Break", "label": "Accounts"},
        {"fieldname": "exchange_profit_loss_account", "fieldtype": "Link", "options": "Account", "label": "Exchange Profit/Loss"},
        {"fieldname": "cash_over_short_account", "fieldtype": "Link", "options": "Account", "label": "Cash Over/Short"},
        {"fieldname": "rounding_account", "fieldtype": "Link", "options": "Account", "label": "Rounding Account"},
        {"fieldname": "cash_in_transit_account", "fieldtype": "Link", "options": "Account", "label": "Cash-in-Transit Account"},
        {"fieldname": "per_currency_customer_receivable", "fieldtype": "Link", "options": "Account", "label": "Per-Currency Customer Receivable Root"},
        
        {"fieldname": "trading_section", "fieldtype": "Section Break", "label": "Trading Rules"},
        {"fieldname": "quote_validity_minutes", "fieldtype": "Int", "label": "Quote Validity Minutes", "default": "3"},
        {"fieldname": "allowed_custom_rate_band", "fieldtype": "Percent", "label": "Allowed Custom Rate Band (± %)"},
        {"fieldname": "min_spread_guard", "fieldtype": "Currency", "label": "Min Spread Guard"},
        {"fieldname": "variance_tolerance", "fieldtype": "Currency", "label": "Variance Tolerance Per Currency"},
        
        {"fieldname": "compliance_section", "fieldtype": "Section Break", "label": "Compliance Limits"},
        {"fieldname": "traveler_limit_usd", "fieldtype": "Currency", "label": "Traveler Limit (USD)"},
        {"fieldname": "traveler_limit_period", "fieldtype": "Select", "options": "\nTransaction\nDay\nYear", "label": "Traveler Limit Period"},
        
        {"fieldname": "receipt_section", "fieldtype": "Section Break", "label": "Receipt Setup"},
        {"fieldname": "receipt_header", "fieldtype": "Text", "label": "Receipt Header"},
        {"fieldname": "receipt_footer", "fieldtype": "Text", "label": "Receipt Footer"}
    ])
    doc.save()
    print("Updated Payment Store Settings")

def update_cashbox():
    doc = frappe.get_doc("DocType", "Cashbox")
    doc.fields = []
    doc.extend("fields", [
        {"fieldname": "cashbox_name", "fieldtype": "Data", "label": "Name", "reqd": 1, "unique": 1},
        {"fieldname": "branch", "fieldtype": "Link", "options": "Branch", "label": "Branch"},
        {"fieldname": "iqd_account", "fieldtype": "Link", "options": "Account", "label": "IQD Account", "reqd": 1},
        {"fieldname": "usd_account", "fieldtype": "Link", "options": "Account", "label": "USD Account", "reqd": 1},
        {"fieldname": "assigned_users", "fieldtype": "Table", "options": "Cashbox User", "label": "Assigned Users"},
        {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"},
        {"fieldname": "locked_until", "fieldtype": "Datetime", "label": "Locked Until", "read_only": 1}
    ])
    doc.save()
    print("Updated Cashbox")

def update_exchange_deal():
    doc = frappe.get_doc("DocType", "Exchange Deal")
    doc.fields = []
    doc.extend("fields", [
        {"fieldname": "deal_type", "fieldtype": "Select", "options": "Sell\nBuy", "label": "Deal Type", "reqd": 1},
        {"fieldname": "deal_mode", "fieldtype": "Select", "options": "Official\nCustom", "label": "Deal Mode", "reqd": 1},
        {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1, "default": "USD"},
        {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "reqd": 1},
        {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
        
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "reqd": 1},
        {"fieldname": "rate_source", "fieldtype": "Select", "options": "Board\nManual", "label": "Rate Source", "reqd": 1},
        {"fieldname": "usd_amount", "fieldtype": "Currency", "label": "USD Amount", "reqd": 1},
        {"fieldname": "iqd_amount", "fieldtype": "Currency", "label": "IQD Amount", "reqd": 1},
        {"fieldname": "last_edited_field", "fieldtype": "Select", "options": "usd_amount\niqd_amount", "label": "Last Edited Field", "default": "usd_amount"},
        
        {"fieldname": "payment_section", "fieldtype": "Section Break"},
        {"fieldname": "payment_mode", "fieldtype": "Select", "options": "Cash\nOn account\nPartial", "label": "Payment Mode", "default": "Cash"},
        {"fieldname": "paid_amount", "fieldtype": "Currency", "label": "Paid Amount"},
        {"fieldname": "rounding_diff", "fieldtype": "Currency", "label": "Rounding Diff", "read_only": 1},
        
        {"fieldname": "accounting_section", "fieldtype": "Section Break", "label": "Accounting"},
        {"fieldname": "cost_rate", "fieldtype": "Currency", "label": "Cost Rate (WAC)", "read_only": 1},
        {"fieldname": "profit_iqd", "fieldtype": "Currency", "label": "Profit (IQD)", "read_only": 1},
        {"fieldname": "wac_before", "fieldtype": "Currency", "label": "WAC Before", "read_only": 1},
        {"fieldname": "wac_after", "fieldtype": "Currency", "label": "WAC After", "read_only": 1},
        {"fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "label": "Journal Entry", "read_only": 1},
        
        {"fieldname": "compliance_section", "fieldtype": "Section Break", "label": "Compliance & Approvals"},
        {"fieldname": "approval_status", "fieldtype": "Select", "options": "Not required\nPending\nApproved\nRejected", "label": "Approval Status", "default": "Not required"},
        {"fieldname": "approval_reason", "fieldtype": "Small Text", "label": "Approval Reason"},
        {"fieldname": "compliance_flags", "fieldtype": "Code", "options": "JSON", "label": "Compliance Flags", "read_only": 1},
        
        {"fieldname": "system_section", "fieldtype": "Section Break"},
        {"fieldname": "quote_id", "fieldtype": "Data", "label": "Quote ID", "read_only": 1},
        {"fieldname": "idempotency_key", "fieldtype": "Data", "label": "Idempotency Key", "unique": 1, "read_only": 1}
    ])
    doc.save()
    print("Updated Exchange Deal")

def update_cashbox_transaction():
    doc = frappe.get_doc("DocType", "Cashbox Transaction")
    doc.fields = []
    doc.extend("fields", [
        {"fieldname": "type", "fieldtype": "Select", "label": "Type", "reqd": 1, "options": "Opening\nCash In\nCash Out\nExpense\nCapital Injection\nCustomer Deposit\nCustomer Withdrawal\nCustomer Receipt\nCustomer Payment\nTransfer\nCounterfeit Write-off"},
        {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
        {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "label": "Currency", "reqd": 1},
        {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1},
        {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate"},
        {"fieldname": "party", "fieldtype": "Dynamic Link", "options": "party_type", "label": "Party"},
        {"fieldname": "party_type", "fieldtype": "Link", "options": "DocType", "label": "Party Type"},
        {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},
        {"fieldname": "attachment", "fieldtype": "Attach", "label": "Attachment"},
        {"fieldname": "transfer_status", "fieldtype": "Select", "options": "\nSent\nConfirmed", "label": "Transfer Status", "depends_on": "eval:doc.type=='Transfer'"},
        {"fieldname": "destination_cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Destination Cashbox", "depends_on": "eval:doc.type=='Transfer'"},
        {"fieldname": "idempotency_key", "fieldtype": "Data", "label": "Idempotency Key", "unique": 1, "read_only": 1}
    ])
    doc.save()
    print("Updated Cashbox Transaction")

def create_cashbox_closing():
    dt = "Cashbox Closing"
    if not frappe.db.exists("DocType", dt):
        frappe.get_doc({
            "doctype": "DocType", "name": dt, "module": "Payment Store", "custom": 0, "is_submittable": 1,
            "naming_rule": "Expression", "autoname": "format:CBC-{YYYY}-{MM}-{#####}",
            "fields": [
                {"fieldname": "cashbox", "fieldtype": "Link", "options": "Cashbox", "label": "Cashbox", "reqd": 1},
                {"fieldname": "cutoff_datetime", "fieldtype": "Datetime", "label": "Cutoff Datetime", "reqd": 1, "default": "Now"},
                {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nPending Approval\nApproved\nRejected\nSubmitted", "label": "Status", "default": "Draft"},
                
                {"fieldname": "counts_section", "fieldtype": "Section Break", "label": "Blind Count"},
                {"fieldname": "counts", "fieldtype": "Table", "options": "Closing Count Row", "label": "Counts"},
                
                {"fieldname": "reconciliation_section", "fieldtype": "Section Break", "label": "Reconciliation"},
                {"fieldname": "counted_totals", "fieldtype": "Code", "options": "JSON", "label": "Counted Totals", "read_only": 1},
                {"fieldname": "expected", "fieldtype": "Code", "options": "JSON", "label": "Expected Balances", "read_only": 1},
                {"fieldname": "variance", "fieldtype": "Code", "options": "JSON", "label": "Variance", "read_only": 1},
                
                {"fieldname": "approval_section", "fieldtype": "Section Break", "label": "Approvals"},
                {"fieldname": "reason", "fieldtype": "Small Text", "label": "Variance Reason"},
                {"fieldname": "approved_by", "fieldtype": "Link", "options": "User", "label": "Approved By", "read_only": 1},
                
                {"fieldname": "system_section", "fieldtype": "Section Break"},
                {"fieldname": "explainer_result", "fieldtype": "Code", "options": "JSON", "label": "Explainer Result", "read_only": 1},
                {"fieldname": "z_report_hash", "fieldtype": "Data", "label": "Z-Report Hash", "read_only": 1}
            ],
            "permissions": [{"role": "Payment Store Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1}, {"role": "Payment Store Cashier", "read": 1, "write": 1, "create": 1, "submit": 1}]
        }).insert(ignore_permissions=True)
        print(f"Created {dt}")
