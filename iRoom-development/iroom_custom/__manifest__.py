# -*- coding: utf-8 -*-
{
    'name': "IRoom Custom",
    'summary': "IRoom Custom",
    'description': """IRoom Custom""",
    'author': "Ahmed Gaber",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr', 'hotel', 'hotel_management', 'ab_hotel_dashboard', 'hotel_laundry', 'iroom_hotel', 'banquet_managment', 'hotel_transport_management'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/hotel_room.xml',
        'views/hotel_reservation.xml',
        'views/hotel_folio.xml',
        'views/res_partner.xml',
        'views/product.xml',
        'wizards/create_future_reservation.xml',
    ],
}

