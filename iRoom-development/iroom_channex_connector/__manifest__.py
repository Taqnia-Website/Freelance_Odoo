# -*- coding: utf-8 -*-
{
    'name': "IRoom Channex Connector",
    'summary': "IRoom Channex Connector",
    'description': """IRoom Channex Connector""",
    'author': "Ahmed Gaber",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hotel', 'hotel_management', 'iroom_hotel'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/res_company.xml',
        'views/sale_shop.xml',
        'views/hotel_room_type.xml',
        'views/product_pricelist.xml',
        'views/hotel_reservation.xml',
        'views/review.xml',
        'wizards/channex_update_rate.xml',
        'wizards/channex_update_availability.xml',
    ],
}
