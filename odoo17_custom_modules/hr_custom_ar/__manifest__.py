{
    "name": "HR  (سلف/خصومات/إضافي/إجازات)",
    "summary": "نماذج الموارد البشرية وربطها بالمحاسبة + تقارير PDF/Excel ولوحات تحكم",
    "version": "17.0.1.0.0",
    "author": "Delivered by ChatGPT",
    "website": "https://example.com",
    "license": "LGPL-3",
    "category": "Human Resources",
    "depends": ["base", "hr", "account"],

    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequences.xml",

        "views/hr_loan_views.xml",
        "views/hr_deduction_views.xml",
        "views/hr_overtime_views.xml",
        "views/hr_leave_views.xml",
        "views/hr_resumption_views.xml",
        "views/hr_resignation_views.xml",
        "views/hr_payroll_sheet_views.xml",
        "views/menu.xml",

        "report/hr_report_templates.xml",
        "report/hr_reports.xml",
        "report/hr_payroll_sheet_report.xml",
    ],
    "application": True,
    "installable": True,
}