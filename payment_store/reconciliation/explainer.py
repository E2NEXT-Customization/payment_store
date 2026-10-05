import frappe
from frappe.utils import flt

def run_explainer(closing_doc):
    """
    Treats every transaction as a vector (ΔIQD, ΔUSD) and searches for 
    known error signatures that match the variance.
    """
    variance = frappe.parse_json(closing_doc.variance) if closing_doc.variance else {}
    usd_var = flt(variance.get('USD'))
    iqd_var = flt(variance.get('IQD'))
    
    if usd_var == 0 and iqd_var == 0:
        return {"status": "ok", "message": "لا توجد فروقات."}
        
    suspects = []
    
    # 1. Missing deal check
    deals = frappe.get_all("Exchange Deal", filters={"cashbox": closing_doc.cashbox, "docstatus": 1, "creation": [">=", frappe.utils.add_days(closing_doc.cutoff_datetime, -1)]}, fields=["name", "deal_type", "usd_amount", "iqd_amount"])
    
    for d in deals:
        d_usd = flt(d.usd_amount) * (1 if d.deal_type == "Buy" else -1)
        d_iqd = flt(d.iqd_amount) * (-1 if d.deal_type == "Buy" else 1)
        
        # Missing deal
        if abs(usd_var + d_usd) < 0.1 and abs(iqd_var + d_iqd) < 100:
            suspects.append({"reason": "صفقة مفقودة أو لم يتم إدخالها", "suspect": d.name, "score": 90})
            
        # Duplicate deal
        if abs(usd_var - d_usd) < 0.1 and abs(iqd_var - d_iqd) < 100:
            suspects.append({"reason": "صفقة مكررة", "suspect": d.name, "score": 90})
            
        # Buy/Sell direction swap
        if abs(usd_var - (2 * d_usd)) < 0.1 and abs(iqd_var - (2 * d_iqd)) < 100:
            suspects.append({"reason": "تم عكس اتجاه الصفقة (بيع بدلاً من شراء أو العكس)", "suspect": d.name, "score": 95})

    # Fallback if no exact match
    if not suspects:
        if usd_var == 0 and abs(iqd_var) > 0:
            suspects.append({"reason": "خطأ في سعر الصرف لإحدى الصفقات أو فرق مدور", "score": 50})
        elif iqd_var == 0 and abs(usd_var) > 0:
            suspects.append({"reason": "تم تسليم/استلام دولارات خاطئة", "score": 50})
        else:
            suspects.append({"reason": "أخطاء متعددة أو عملية غير مسجلة كلياً", "score": 30})
            
    suspects = sorted(suspects, key=lambda x: x.get('score', 0), reverse=True)
    return suspects
