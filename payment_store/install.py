import frappe

def after_install():
    create_roles()
    create_workspace()

def create_roles():
    roles = ["Payment Store Manager", "Payment Store Cashier", "Payment Store Auditor"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            doc = frappe.new_doc("Role")
            doc.role_name = role_name
            doc.desk_access = 1
            doc.insert(ignore_permissions=True)

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
