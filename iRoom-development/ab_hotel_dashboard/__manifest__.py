# -*- coding: utf-8 -*-
{
    'name': "Hotel Dashboard",

    'summary': "Hotel Dashboard",

    'description': """
Hotel Dashboard    """,

    'author': "Abdalmola Mustafa",
    'website': "https://www.abdalmola-apps.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hotel_dashboard'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # '/ab_hotel_dashboard/static/src/js/apexcharts.min.js',
            '/ab_hotel_dashboard/static/src/js/reservation.js',
            '/ab_hotel_dashboard/static/src/js/libs/chart.umd.min.js',
            '/ab_hotel_dashboard/static/src/xml/reservation.xml',
            '/ab_hotel_dashboard/static/src/css/reservation.css',
            '/ab_hotel_dashboard/static/src/css/reservation.scss',
        ],
    },
}
