import frappe
import json

def execute():
    workspace_name = "Payment Store"
    block_name = "Payment Store Shortcuts HTML"
    
    html_content = """
    <style>
    .ps-dashboard-container {
        padding: 20px;
        background: #f4f5f7;
        border-radius: 12px;
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    .ps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    .ps-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-decoration: none !important;
        color: #333;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid #eaeaea;
    }
    .ps-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    .ps-icon {
        font-size: 30px;
        margin-bottom: 10px;
    }
    .ps-icon.green { color: #2ecc71; }
    .ps-icon.blue { color: #3498db; }
    .ps-icon.orange { color: #f39c12; }
    .ps-icon.red { color: #e74c3c; }
    .ps-icon.gray { color: #7f8c8d; }
    
    .ps-card-title {
        font-size: 16px;
        font-weight: 600;
    }
    </style>

    <div class="ps-dashboard-container">
        <h3 style="margin: 0; color: #2c3e50; font-weight: bold;">بوابة نظام الصرافة</h3>
        <p style="color: #7f8c8d; margin-top: 5px;">اختر من العمليات أدناه للبدء السريع</p>
        
        <div class="ps-grid">
            <a href="/app/ps-official-sale" class="ps-card">
                <div class="ps-icon blue">💵</div>
                <div class="ps-card-title">بيع دولار (رسمي)</div>
            </a>
            <a href="/app/ps-custom-sale" class="ps-card">
                <div class="ps-icon orange">💸</div>
                <div class="ps-card-title">بيع دولار (خاص)</div>
            </a>
            <a href="/app/ps-buy-desk" class="ps-card">
                <div class="ps-icon green">💰</div>
                <div class="ps-card-title">شراء دولار</div>
            </a>
            <a href="/app/ps-cash-desk" class="ps-card">
                <div class="ps-icon gray">🏦</div>
                <div class="ps-card-title">نافذة القاصة</div>
            </a>
            <a href="/app/ps-closing-desk" class="ps-card">
                <div class="ps-icon red">⚖️</div>
                <div class="ps-card-title">الجرد والإغلاق</div>
            </a>
            <a href="/app/exchange-deal" class="ps-card">
                <div class="ps-icon blue">📋</div>
                <div class="ps-card-title">سجل الصفقات</div>
            </a>
            <a href="/app/cashbox-transaction" class="ps-card">
                <div class="ps-icon gray">📝</div>
                <div class="ps-card-title">حركات القاصة</div>
            </a>
            <a href="/app/payment-store-settings" class="ps-card">
                <div class="ps-icon gray">⚙️</div>
                <div class="ps-card-title">الإعدادات</div>
            </a>
        </div>
    </div>
    """

    if not frappe.db.exists("Custom HTML Block", block_name):
        frappe.get_doc({
            "doctype": "Custom HTML Block",
            "name": block_name,
            "html": html_content,
            "private": 0
        }).insert(ignore_permissions=True)
    else:
        doc = frappe.get_doc("Custom HTML Block", block_name)
        doc.html = html_content
        doc.save(ignore_permissions=True)

    ws = frappe.get_doc("Workspace", workspace_name)
    
    # Check if we already have the custom HTML block in the workspace JSON
    content = []
    if ws.content:
        content = json.loads(ws.content)
        
    has_html_block = any(b.get("type") == "custom_html" and b.get("data", {}).get("html_block_name") == block_name for b in content)
    
    if not has_html_block:
        new_block = {
            "id": frappe.generate_hash(length=10),
            "type": "custom_html",
            "data": {
                "html_block_name": block_name
            }
        }
        # Insert at the beginning
        content.insert(0, new_block)
        ws.content = json.dumps(content)
        ws.save(ignore_permissions=True)
        
    frappe.db.commit()
    print("Beautiful HTML Workspace installed.")
