{
    'name': 'Debrand Module Bizople',
    'category': 'Extra Tools',
    'version': '17.0.0.1',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com/',
    'summary': 'The ultimate base odoo backend debranding module.',
    'description': """ The ultimate base odoo backend debranding module.""",
    'depends': ['web', 'website', 'mail', 'portal', 'auth_signup', 'digest', 'snailmail_account','crm','hr_skills','product','point_of_sale'],
    'data': [
        'data/demo_data.xml',
        'data/email_template_layout.xml',
        'data/portal_mail_template_data.xml',
        'data/digest_data.xml',
        'data/digest_tips_data.xml',
        'data/auth_signup_mail_template_data.xml',
        'views/auth_signup_mail_template.xml',
        'views/res_config_settings_view.xml',
        'views/digest_view_inherit.xml',
        'views/ir_module_views.xml',
        'views/web_login_template.xml',
        'views/portal_sidebar_template.xml',
        'views/res_company_view.xml',
        'views/crm_lead_view.xml',
        'views/res_partner_view.xml',
        'views/hr_views.xml',
        'views/product_views.xml',
        'views/calendar_views.xml',
        'views/pos_assets_index.xml'

    ],
    'assets': {
        'web.assets_backend': [
            ('include', 'web._assets_helpers'),
            ('include', 'web._assets_backend_helpers'),
            '/odoo_debrand_biz/static/src/js/page_title.js',
            '/odoo_debrand_biz/static/src/js/dialog.js',
            '/odoo_debrand_biz/static/src/js/erorr_dialog.js',
            '/odoo_debrand_biz/static/src/scss/doc_link.scss',
            '/odoo_debrand_biz/static/src/xml/upgrade_dialog.xml',
            '/odoo_debrand_biz/static/src/xml/notification_alert.xml',
            '/odoo_debrand_biz/static/src/xml/user_menu.xml',
            
        ],
        'point_of_sale._assets_pos': [
            '/odoo_debrand_biz/static/src/xml/pos_navbar.xml',
            '/odoo_debrand_biz/static/src/xml/pos_order_receipt.xml'
        ],
        'web.assets_frontend': [
            '/odoo_debrand_biz/static/src/js/erorr_dialog.js',
        ],

    },
    'images': [
    ],
    'sequence': 1,
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
