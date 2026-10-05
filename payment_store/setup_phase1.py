import frappe

def create_roles():
    roles = ["Payment Store Manager", "Payment Store Cashier", "Payment Store Auditor"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            doc = frappe.new_doc("Role")
            doc.role_name = role_name
            doc.desk_access = 1
            doc.insert(ignore_permissions=True)
            print(f"Created Role: {role_name}")

def create_doctype():
    doctype_name = "Payment Store Settings"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Payment Store",
            "custom": 0,
            "issingle": 1,
            "fields": [
                {
                    "fieldname": "company",
                    "fieldtype": "Link",
                    "label": "Company",
                    "options": "Company",
                    "reqd": 1
                },
                {
                    "fieldname": "iqd_rounding_step",
                    "fieldtype": "Select",
                    "label": "IQD Rounding Step",
                    "options": "1\n250\n500\n1000",
                    "default": "250"
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1
                },
                {
                    "role": "Payment Store Manager",
                    "read": 1,
                    "write": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created DocType: {doctype_name}")

def create_workspace():
    workspace_name = "Payment Store"
    if not frappe.db.exists("Workspace", workspace_name):
        doc = frappe.get_doc({
            "doctype": "Workspace",
            "name": workspace_name,
            "label": workspace_name,
            "title": workspace_name,
            "module": "Payment Store",
            "type": "Workspace",
            "roles": [{"role": "Payment Store Manager"}, {"role": "Payment Store Cashier"}]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created Workspace: {workspace_name}")

def execute():
    try:
        create_roles()
        create_doctype()
        create_workspace()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e
