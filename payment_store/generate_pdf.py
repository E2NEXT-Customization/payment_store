import frappe
from frappe.utils.pdf import get_pdf
import os

def execute():
    html_content = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'Tajawal', Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
                direction: rtl;
                text-align: right;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                text-align: center;
            }
            h2 {
                color: #2980b9;
                margin-top: 30px;
            }
            h3 {
                color: #16a085;
            }
            p {
                font-size: 14px;
            }
            ul {
                margin-right: 20px;
                font-size: 14px;
            }
            li {
                margin-bottom: 8px;
            }
            .cover {
                text-align: center;
                margin-top: 100px;
                margin-bottom: 150px;
            }
            .page-break {
                page-break-before: always;
            }
            .note {
                background: #fdfefe;
                border-right: 4px solid #f39c12;
                padding: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="cover">
            <h1 style="border:none; font-size: 36px;">دليل المستخدم - تطبيق الصارم للصرافة</h1>
            <p style="font-size: 20px; color: #7f8c8d;">Payment Store System (ERPNext)</p>
            <p style="margin-top: 50px;">تاريخ الإصدار: 2026</p>
        </div>

        <div class="page-break"></div>

        <h2>مقدمة عن النظام</h2>
        <p>تطبيق <strong>Payment Store</strong> هو نظام متكامل مبني على بيئة Frappe / ERPNext ومصمم خصيصاً لتلبية احتياجات شركة الصارم للصرافة في العراق. يدعم النظام العملات المزدوجة (الدينار العراقي والدولار الأمريكي)، ويقدم واجهات سريعة وسهلة الاستخدام لعمليات البيع والشراء والجرد اليومي.</p>

        <h2>1. واجهات البيع والشراء (Deals)</h2>
        <p>يحتوي النظام على ثلاث واجهات رئيسية للتعامل مع العملاء:</p>
        <ul>
            <li><strong>بيع دولار (رسمي):</strong> مخصصة لبيع الدولار بالسعر الرسمي الثابت. (لا يمكن تغيير سعر الصرف يدوياً من هذه الشاشة للحفاظ على السياسة النقدية).</li>
            <li><strong>بيع دولار (خاص):</strong> مخصصة لبيع الدولار للعملاء بسعر يتم الاتفاق عليه لحظياً.</li>
            <li><strong>شراء دولار:</strong> مخصصة لشراء الدولار من العملاء (تزويد القاصة بالدولار مقابل الدينار).</li>
        </ul>
        <div class="note">
            <strong>ملاحظة:</strong> النظام يقوم بحساب متوسط التكلفة المرجح (WAC) تلقائياً لكل حركة، ويقوم بتوليد قيود يومية (Journal Entries) خلف الكواليس لضمان الترابط المحاسبي.
        </div>

        <h2>2. واجهة القاصة (Cash Desk)</h2>
        <p>شاشة مخصصة لأمناء الصندوق (الكاشير) لتسجيل الحركات المالية التي لا تعتبر صفقات بيع أو شراء، مثل:</p>
        <ul>
            <li><strong>الإيداع والسحب النقدي العادي:</strong> لتمويل أو سحب السيولة.</li>
            <li><strong>المصاريف:</strong> تسجيل النفقات اليومية وسحبها مباشرة من القاصة.</li>
            <li><strong>أمانات العملاء:</strong> استلام أموال من العملاء للاحتفاظ بها أو تسليمها لهم لاحقاً.</li>
            <li><strong>التحويل بين القاصات (Transfers):</strong> يسمح بتحويل الأموال من قاصة لأخرى (مثل تحويل من الفرع الرئيسي إلى فرع A). التحويل يتم بنظام الخطوتين للحفاظ على الأموال في حالة (Cash in Transit) حتى يتم استلامها وتأكيدها.</li>
        </ul>

        <h2>3. الجرد والإغلاق (Cashbox Closing & Explainer)</h2>
        <p>هذه الشاشة هي قلب الرقابة في النظام. في نهاية اليوم، يقوم الكاشير بعملية الإغلاق كالتالي:</p>
        <ul>
            <li>يقوم بإدخال الجرد الفعلي للمبالغ النقدية الموجودة في الدرج (الجرد الأعمى).</li>
            <li>يقوم النظام فوراً بمقارنة المبالغ المدخلة مع الرصيد الدفتري (GL Balance) في النظام.</li>
            <li>في حال وجود فروقات (نقص أو زيادة)، يتم تشغيل محرك <strong>Explainer Engine</strong> الذكي.</li>
        </ul>
        <h3>محرك Explainer (مكتشف الأخطاء):</h3>
        <p>عند وجود فرق في الجرد، يقوم النظام بالبحث في صفقات اليوم وتحليلها رياضياً ليقترح على المدير أسباب النقص، مثل: (احتمال وجود صفقة لم تُسجل، صفقة سُجلت مرتين، خطأ في إدخال سعر الصرف، إلخ).</p>
        <div class="note">
            يتم ختم مستند الإغلاق بتشفير Hash خاص يشبه الـ Z-Report لضمان عدم التلاعب به بعد إصداره.
        </div>

        <div class="page-break"></div>

        <h2>4. التقارير ولوحات المتابعة</h2>
        <p>يحتوي النظام على تقارير مالية جاهزة للإدارة:</p>
        <ul>
            <li><strong>كشف حساب العميل:</strong> لمتابعة كل تعاملات عميل محدد.</li>
            <li><strong>التداول اليومي:</strong> تقرير يجمع كل صفقات البيع والشراء التي تمت خلال اليوم.</li>
            <li><strong>أنماط الفروقات (Variance Patterns):</strong> تقرير يوضح انحرافات الجرد اليومية لكل قاصة لتقييم أداء الكاشير.</li>
        </ul>

        <h2>5. الإعدادات الأساسية (Settings)</h2>
        <p>شاشة الإعدادات <strong>Payment Store Settings</strong> هي لوحة التحكم الرئيسية للمدير، ومنها يمكن تحديد:</p>
        <ul>
            <li>الحسابات المحاسبية الافتراضية (حساب الأرباح والخسائر، حساب الأموال في الطريق).</li>
            <li>العملات المدعومة وتتبع الكمية المتوفرة ومتوسط التكلفة لكل عملة.</li>
        </ul>

        <h2 style="text-align: center; margin-top: 80px; color: #7f8c8d;">--- نهاية الدليل ---</h2>
    </body>
    </html>
    """

    pdf = get_pdf(html_content, {"orientation": "Portrait", "page-size": "A4"})
    
    file_path = os.path.join(frappe.utils.get_site_path(), "public", "files", "Payment_Store_Guide.pdf")
    
    with open(file_path, "wb") as f:
        f.write(pdf)
        
    print(f"PDF generated successfully at {file_path}")
