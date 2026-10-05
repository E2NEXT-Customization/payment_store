import frappe

def execute():
    try:
        create_roles()
        grant_roles_to_all_users()
        create_workspace()
        frappe.db.commit()
        print("Workspace and Roles successfully configured.")
    except Exception as e:
        frappe.db.rollback()
        raise e

def create_roles():
    roles = ["Payment Store Manager", "Payment Store Cashier", "Payment Store Auditor"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": 1
            }).insert(ignore_permissions=True)
            print(f"Created Role: {role}")

def grant_roles_to_all_users():
    users = frappe.get_all("User", filters={"user_type": "System User", "name": ["!=", "Administrator"]})
    
    # Also add to Administrator explicitly just in case
    users.append({"name": "Administrator"})
    
    for user_info in users:
        user = frappe.get_doc("User", user_info.get("name") or user_info["name"])
        existing_roles = [r.role for r in user.roles]
        
        roles_to_add = ["Payment Store Manager", "Payment Store Cashier"]
        added = False
        for role in roles_to_add:
            if role not in existing_roles:
                user.append("roles", {"role": role})
                added = True
        
        if added:
            user.flags.ignore_permissions = True
            user.save()
            print(f"Granted roles to User: {user.name}")

def create_workspace():
    workspace_name = "Payment Store"
    if frappe.db.exists("Workspace", workspace_name):
        frappe.delete_doc("Workspace", workspace_name, force=True)

    links = [
        # Pages (Desks)
        {"type": "Link", "link_to": "ps-official-sale", "label": "بيع دولار – سعر رسمي", "link_type": "Page"},
        {"type": "Link", "link_to": "ps-custom-sale", "label": "بيع دولار – سعر خاص", "link_type": "Page"},
        {"type": "Link", "link_to": "ps-buy-desk", "label": "شراء دولار", "link_type": "Page"},
        {"type": "Link", "link_to": "ps-cash-desk", "label": "القاصة", "link_type": "Page"},
        {"type": "Link", "link_to": "ps-closing-desk", "label": "الجرد والإغلاق", "link_type": "Page"},
        {"type": "Link", "link_to": "ps-control-tower", "label": "برج المراقبة", "link_type": "Page"},
        
        # DocTypes
        {"type": "Link", "link_to": "Exchange Deal", "label": "Deals", "link_type": "DocType"},
        {"type": "Link", "link_to": "Cashbox Transaction", "label": "Transactions", "link_type": "DocType"},
        {"type": "Link", "link_to": "Cashbox Closing", "label": "Closings", "link_type": "DocType"},
        {"type": "Link", "link_to": "Cashbox", "label": "Cashboxes", "link_type": "DocType"},
        {"type": "Link", "link_to": "PS Daily Rate", "label": "Daily Rates", "link_type": "DocType"},
        {"type": "Link", "link_to": "Payment Store Settings", "label": "Settings", "link_type": "DocType"}
    ]

    frappe.get_doc({
        "doctype": "Workspace",
        "name": workspace_name,
        "label": workspace_name,
        "title": workspace_name,
        "module": "Payment Store",
        "is_standard": 1,
        "public": 1,
        "for_user": "",
        "sequence_id": 1,
        "links": links
    }).insert(ignore_permissions=True)
    print(f"Created Workspace: {workspace_name}")
