from odoo import http
from odoo.http import request

from datetime import datetime
import pytz
import math


class HomeController(http.Controller):
    @http.route('/search_hotels', website=True, type='http', methods=['POST', 'GET'], auth='public')
    def search_hotels(self, **kwargs):
        all_hotels = request.env['sale.shop'].sudo().with_context(lang=request.context['lang']).search([])
        all_amenities = request.env['hotel.room_amenities'].sudo().with_context(lang=request.context['lang']).search([])
        values = {
            'all_hotels': [{'id': hotel.id, 'name': hotel.name} for hotel in all_hotels],
            'all_amenities_1': [{'id': amenity.id, 'name': amenity.name} for amenity in all_amenities[:int(len(all_amenities)/2)]]
        }
        if len(all_amenities) > 1:
            values['all_amenities_2'] = [{'id': amenity.id, 'name': amenity.name} for amenity in all_amenities[int(len(all_amenities)/2):]]

        rooms = self._get_searchable_rooms(kwargs)
        result = self._get_result(rooms['rooms'])
        values['rooms'] = result

        values['number_of_pages'] = rooms['number_of_pages']
        values['page'] = rooms['page']
        values['inputs'] = kwargs
        if kwargs.get('price'):
            values['inputs']['price_from'], values['inputs']['price_to'] = kwargs['price'].split(';')

        return request.render('iroom_website.search_page_template', values)

    def _get_searchable_rooms(self, data):
        domain = []

        if data['hotel_select'] != '0' and not data['hotel_select'] == '':
            domain.append(('shop_id', '=', int(data['hotel_select'])))
        if data.get('location'):
            domain.append(('shop_id.address', 'ilike', data['location']))
        if data.get('number_of_adults') and data.get('number_of_adults') != '0':
            domain.append(('max_adult', '>=', int(data['number_of_adults'])))
        if data.get('number_of_children') and data.get('number_of_adults') != '0':
            domain.append(('max_child', '>=', int(data['number_of_children'])))
        if data.get('price'):
            min_price, max_price = data['price'].split(';')
            domain.extend([('list_price', '>=', int(min_price)), ('list_price', '<=', int(max_price))])
        amenities = [key for key, value in data.items() if 'amenity_' in key]
        amenities = [amenity.split('_')[1] for amenity in amenities]
        if amenities:
            domain.append(('room_amenities.name', 'in', amenities))
        ratings = [key for key, value in data.items() if 'stars_' in key]
        ratings = [rating.split('_')[1] for rating in ratings]
        if ratings:
            min_rating = float(min(ratings))
            match_ratings = request.env['hotel.reservation.rating'].sudo().search([('total_rate', '>=', min_rating)])
            if match_ratings:
                hotels = match_ratings.mapped('shop_id')
                domain.append(('shop_id', 'in', hotels.ids))
        if data.get('dates') or data.get('from_date') or data.get('to_date'):
            if data.get('dates'):
                checkin, checkout = data['dates'].split(' - ')
                checkin = datetime.strptime(checkin, '%m/%d/%Y')
                checkin = pytz.timezone(request.env.user.tz or 'UTC').localize(checkin).astimezone(pytz.utc).replace(tzinfo=None)
                checkout = datetime.strptime(checkout, '%m/%d/%Y')
                checkout = pytz.timezone(request.env.user.tz or 'UTC').localize(checkout).astimezone(pytz.utc).replace(tzinfo=None)
            else:
                checkin = data.get('from_date')
                checkout = data.get('to_date')
                checkin = datetime.strptime(checkin, '%Y-%m-%d')
                checkin = pytz.timezone(request.env.user.tz or 'UTC').localize(checkin).astimezone(pytz.utc).replace(tzinfo=None)
                checkout = datetime.strptime(checkout, '%Y-%m-%d')
                checkout = pytz.timezone(request.env.user.tz or 'UTC').localize(checkout).astimezone(pytz.utc).replace(tzinfo=None)
            reserved_lines = request.env['hotel.reservation.line'].sudo().search([
                ('line_id.state', '=', 'confirm'),
                ('checkin', '<=', checkin), ('checkout', '>=', checkin),
                '|',
                ('checkout', '<=', checkout), ('checkin', '<=', checkout)
            ])
            if reserved_lines:
                reserved_products = reserved_lines.mapped('room_number')
                reserved_rooms = request.env['hotel.room'].sudo().search([('product_id', 'in', reserved_products.ids)])
                domain.append(('id', 'not in', reserved_rooms.ids))

        limit = 6
        page = int(data.get('page') if data.get('page') else 1)
        offset = (limit * page) - limit

        rooms = request.env['hotel.room'].sudo().with_context(lang=request.context['lang']).search(domain, offset=offset)
        if data.get('order_by'):
            if data['order_by'] == 'popularity':
                rooms = rooms.sorted(lambda r: (r.shop_id.reservation_count, r.id), True)
            elif data['order_by'] == 'rating_average':
                rooms = rooms.sorted(lambda r: (r.shop_id.rating_average, r.id), True)
            elif data['order_by'] == 'price_down':
                rooms = rooms.sorted('list_price')
            elif data['order_by'] == 'price_up':
                rooms = rooms.sorted('list_price', True)
        rooms = rooms[0:limit]


        available_rooms_count = request.env['hotel.room'].sudo().with_context(lang=request.context['lang']).search_count(domain)
        number_of_pages = math.ceil(available_rooms_count / limit)

        if 'page=' in request.httprequest.url:
            url = request.httprequest.url
            index_start = url.find('page=')
            index_end = index_start + 6
            new_url = url[:index_start] + url[index_end:]
            request.httprequest.url = new_url

        return {
            'rooms': rooms,
            'number_of_pages': number_of_pages,
            'page': page
        }

    def _get_result(self, rooms):
        result = []
        for room in rooms:
            matched_rating_count = request.env['hotel.reservation.rating'].sudo().search_count([('shop_id', '=', room.shop_id.id)])
            result.append({
                'name': room.name,
                'hotel_name': room.shop_id.name,
                'hotel_url': f'{request.httprequest.host_url}hotel/{room.shop_id.id}',
                'image_url': f'/web/image/hotel.room/{room.id}/image_1920' or '',
                'rating': room.shop_id.rating_average,
                'number_of_ratings': matched_rating_count,
                'address': room.shop_id.address,
                'location': room.shop_id.location,
                'unit_price': room.list_price,
                'description': room.description_sale or ''
            })
        return result
