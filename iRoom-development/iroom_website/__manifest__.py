{
    "name": "IRoom Website",
    "version": "17.0.1.0",
    "depends": ['web', 'website', 'iroom_hotel'],
    "data": [
        'views/hotel-page.xml',
        'views/payment-page.xml',
        'views/components/hotel_components/booking_component.xml',
        'views/components/hotel_components/header_component.xml',
        'views/components/hotel_components/main_component.xml',
        
        'views/components/search_components/filter_component.xml',
        'views/components/search_components/header_component.xml',
        'views/components/search_components/search_component.xml',

        'views/pages/booking.xml',
        'views/pages/hotel_page.xml',
        'views/pages/search_page.xml',
        'views/pages/similar_hotels.xml',

        'views/portal/my_orders.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            # 'iroom_website/static/src/css/*.css',
            # 'iroom_website/static/src/js/lib/jquery.min.js',
            # 'iroom_website/static/src/js/lib/plugins.js',
            # 'iroom_website/static/src/js/lib/scripts.js',
            'iroom_website/static/src/js/components/**/*.js',
            'iroom_website/static/src/js/website/*.js',

        ]
    },
    'license': 'OPL-1'
}
