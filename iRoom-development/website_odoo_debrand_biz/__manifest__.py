# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details
{
    'name': 'Website Debrand Module Bizople',
    'category': 'Extra Tools',
    'version': '17.0.0.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com/',
    'summary': 'The ultimate Website odoo backend debranding module.',
    'description': """ The ultimate Website odoo backend debranding module.""",
    'depends': ['website', 'auth_totp_portal'],
    'data': [
        'templates/remove_odoo_footer.xml',
        'views/two_factor_auth_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/website_odoo_debrand_biz/static/src/scss/website_configrator_page.scss',
        ],
        'web.assets_backend': [
            '/website_odoo_debrand_biz/static/src/scss/website_configrator_page.scss',
        ],
    },
    'images': [
    ],
    'sequence': 1,
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
