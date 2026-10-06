import frappe
import json

def execute():
    workspace_name = "Payment Store"
    
    if not frappe.db.exists("Workspace", workspace_name):
        print(f"Workspace {workspace_name} does not exist.")
        return

    # We don't need 'Workspace Shortcut' doctype. 
    # In Frappe v15, shortcuts in a Workspace can be native editor blocks or child table shortcuts.
    # We will just append them into the "shortcuts" child table.
    
    ws = frappe.get_doc("Workspace", workspace_name)
    ws.shortcuts = [] # clear existing
    ws.links = [] # clear existing sidebar links
    
    items = [
        {"type": "Page", "link_to": "ps-official-sale", "label": "بيع دولار – سعر رسمي", "color": "Blue", "icon": "money"},
        {"type": "Page", "link_to": "ps-custom-sale", "label": "بيع دولار – سعر خاص", "color": "Orange", "icon": "money"},
        {"type": "Page", "link_to": "ps-buy-desk", "label": "شراء دولار", "color": "Green", "icon": "money"},
        {"type": "Page", "link_to": "ps-cash-desk", "label": "القاصة", "color": "Gray", "icon": "safe"},
        {"type": "Page", "link_to": "ps-closing-desk", "label": "الجرد والإغلاق", "color": "Red", "icon": "check"},
        {"type": "DocType", "link_to": "Exchange Deal", "label": "الصفقات (Deals)", "color": "Blue", "icon": "list"},
        {"type": "DocType", "link_to": "Cashbox Transaction", "label": "حركات القاصة (Transactions)", "color": "Gray", "icon": "list"},
        {"type": "DocType", "link_to": "Cashbox Closing", "label": "الإغلاقات (Closings)", "color": "Red", "icon": "list"},
        {"type": "DocType", "link_to": "PS Daily Rate", "label": "أسعار الصرف (Rates)", "color": "Orange", "icon": "list"},
        {"type": "DocType", "link_to": "Payment Store Settings", "label": "الإعدادات (Settings)", "color": "Gray", "icon": "setting"}
    ]
    
    for item in items:
        # Add to Sidebar links
        ws.append("links", {
            "type": "Link",
            "link_to": item["link_to"],
            "label": item["label"],
            "link_type": item["type"]
        })
        
        # Add to shortcuts (Main Dashboard)
        ws.append("shortcuts", {
            "type": item["type"],
            "link_to": item["link_to"],
            "label": item["label"],
            "color": item["color"],
            "icon": item["icon"],
            "format": "Standard"
        })
        
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("Shortcuts added successfully.")
