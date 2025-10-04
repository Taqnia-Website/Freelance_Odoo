from odoo import http
from odoo.http import request

import math


class HomeController(http.Controller):
    @http.route('/booking', website=True, type='http', auth='public')
    def home_controller(self, **kwargs):
        hotel_model = request.env['sale.shop'].sudo().with_context(lang=request.context['lang'])
        room_model = request.env['hotel.room'].sudo().with_context(lang=request.context['lang'])

        all_hotels= hotel_model.search([])
        hotels_data = self._get_hotels(hotel_model, room_model)
        rooms_data = self._get_rooms(room_model, kwargs.get('page'))

        values = {
            'all_hotels': [{
                'id': hotel.id,
                'name': hotel.name
            } for hotel in all_hotels],
            'hotels': hotels_data,
            **rooms_data
        }

        return request.render('iroom_website.booking', values)

    def _get_hotels(self, hotel_model, room_model):
        hotels = hotel_model.search([])
        hotels_data = []
        for hotel in hotels:
            if hotel.description and len(hotel.description) <= 100:
                description = hotel.description
            elif hotel.description and len(hotel.description) > 100:
                description = f'{hotel.description[0:97]}...'
            else:
                description = ''

            rooms = room_model.search([('shop_id', '=', hotel.id)])
            average_nightly_price = sum(rooms.mapped('list_price')) / len(rooms) if rooms else 0.0
            average_nightly_price = round(average_nightly_price * 100) / 100

            hotels_data.append({
                'name': hotel.name,
                'image_url': f'/web/image/sale.shop/{hotel.id}/shop_img' or '',
                'hotel_url': f'{request.httprequest.host_url}hotel/{hotel.id}',
                'address': hotel.address or '',
                'location': hotel.location or '',
                'description': description,
                'rating_average': round(hotel.rating_average * 100) / 100,
                'rating_count': hotel.rating_count,
                'average_nightly_price': average_nightly_price,
                'amenities': [{
                    'name': amenity.name,
                    'icon': amenity.icon_code or ''
                } for amenity in hotel.amenity_ids]
            })

        return hotels_data

    def _get_rooms(self, room_model, page):
        limit = 6
        page = int(page if page else 1)
        offset = (limit * page) - limit

        rooms = room_model.search([], offset=offset, limit=limit)
        rooms_data = []
        for room in rooms:
            if room.description_sale and len(room.description_sale) <= 100:
                description = room.description_sale
            elif room.description_sale and len(room.description_sale) > 100:
                description = f'{room.description_sale[0:97]}...'
            else:
                description = ''

            hotel = room.shop_id

            rooms_data.append({
                'name': room.name,
                'hotel_name': hotel.name,
                'image_url': f'/web/image/hotel.room/{room.id}/image_1920' or '',
                'hotel_url': f'{request.httprequest.host_url}hotel/{hotel.id}',
                'address': hotel.address or '',
                'location': hotel.location or '',
                'description': description,
                'rating_average': hotel.rating_average,
                'rating_count': hotel.rating_count,
                'average_nightly_price': room.list_price,
                'amenities': [{
                    'name': amenity.name,
                    'icon': amenity.icon_code or ''
                } for amenity in room.room_amenities]
            })

        available_rooms_count = room_model.search_count([])
        number_of_pages = math.ceil(available_rooms_count / limit)

        return {
            'rooms': rooms_data,
            'number_of_pages': number_of_pages,
            'page': page
        }
