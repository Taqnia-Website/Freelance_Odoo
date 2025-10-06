{
    "name": "الصيانة (مخصص)",
    "summary": "طلبات صيانة وقطع غيار مع خصم من المخزون وتحويل لفاتورة مشتريات + تقارير PDF/Excel ولوحات تحكم",
    "version": "17.0.1.0.0",
    "author": "Delivered by ChatGPT",
    "website": "https://example.com",
    "license": "LGPL-3",
    "category": "Operations/Inventory",
    "depends": ["base", "stock", "account"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequences.xml",

        "report/maintenance_report_templates.xml",
        "report/maintenance_reports.xml",

        "views/maintenance_request_views.xml",
        "views/menu.xml"
    ],
    "application": True,
    "installable": True,
}
