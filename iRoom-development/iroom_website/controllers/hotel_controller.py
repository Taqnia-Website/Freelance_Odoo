from odoo import http, _
from odoo.http import request

from datetime import datetime
import pytz
import math


class HotelController(http.Controller):
    @http.route('/hotel/<int:id>', website=True, type='http', auth='public')
    def hotel_controller(self, **kwargs):
        hotel = request.env['sale.shop'].sudo().with_context(lang=request.context['lang']).browse(kwargs['id'])
        try:
            values = {
                'id': hotel.id,
                'name': hotel.name,
                'image_url': f'/web/image/sale.shop/{hotel.id}/shop_img' or '',
                'address': hotel.address or '',
                'mobile': hotel.mobile or '',
                'email': hotel.email or '',
                'hotel_website': hotel.website or '',
                'location': hotel.location or '',
                'location_iframe': hotel.location_iframe or '',
                'facebook': hotel.facebook or '',
                'twitter': hotel.twitter or '',
                'vk': hotel.vk or '',
                'instagram': hotel.instagram or '',
                'youtube_link': hotel.youtube_link,
                'description': hotel.description or '',
                'distance_from_center': hotel.distance_from_center,
                'number_of_restaurants': hotel.number_of_restaurants,
                'breakfast': hotel.breakfast or '',
                'lunch': hotel.lunch or '',
                'dinner': hotel.dinner or '',
                'check_in_out_times': hotel.check_in_out_times or '',
                'can_rate': False
            }
        except Exception as e:
            return request.redirect('/not_found')

        rooms_count = request.env['hotel.room'].sudo().search_count([('shop_id', '=', kwargs['id'])])
        values['rooms_count'] = rooms_count

        if hotel.image_ids:
            values['image_urls_1_to_4'] = [f'/web/image/sale.shop.image/{image.id}/image' for image in hotel.image_ids[0:5]]
            if len(hotel.image_ids) > 4:
                values['image_url_5'] = f'/web/image/sale.shop.image/{hotel.image_ids[4].id}/image'
            if len(hotel.image_ids) > 5:
                values['image_urls_rest'] = [{'src': f'/web/image/sale.shop.image/{image.id}/image'} for image in hotel.image_ids[5:]]

        if hotel.amenity_ids:
            values['amenities'] = [{'name': amenity.name, 'icon': amenity.icon_code} for amenity in hotel.amenity_ids]

        if hotel.tag_ids:
            values['tags'] = [tag.name for tag in hotel.tag_ids]

        if hotel.activity_ids:
            values['activities'] = [{
                'name': activity.name or '',
                'distance': activity.distance or '',
                'description': activity.description or '',
                'image_url': f'/web/image/sale.shop.activity.line/{activity.id}/image' or ''
            } for activity in hotel.activity_ids]

        if hotel.similar_hotels_ids:
            values['similar_hotels'] = [{
                'name': similar.name,
                'url': f'/hotel/{similar.id}',
                'image_url': f'/web/image/sale.shop/{similar.id}/shop_img' or '',
                'close_to': similar.close_to
            } for similar in hotel.similar_hotels_ids]

        rooms = request.env['hotel.room'].sudo().with_context(lang=request.context['lang']).search([('shop_id', '=', kwargs['id'])])
        if rooms:
            values['rooms'] = [{
                'id': room.product_id.id,
                'name': room.name,
                'unit_price': room.list_price
            } for room in rooms]

        if not request.env.user._is_public():
            reservation_lines = request.env['hotel.reservation.line'].sudo().search([
                ('line_id.partner_id', '=', request.env.user.partner_id.id),
                ('line_id.shop_id', '=', int(kwargs['id'])),
                ('line_id.state', '=', 'confirm'),
                ('checkin', '<=', datetime.now())
            ])
            reservation_ids = reservation_lines.mapped('line_id').ids
            if reservation_ids:
                ratings = request.env['hotel.reservation.rating'].sudo().search([('reservation_id', 'in', reservation_ids)])
                values['can_rate'] = True if not ratings else False
        else:
            # Signup details
            countries = request.env['res.country'].sudo().with_context(lang=request.context['lang']).search([])
            values['countries'] = [{'id': country.id, 'name': country.name} for country in countries]

        hotel_ratings = request.env['hotel.reservation.rating'].sudo().search([('shop_id', '=', hotel.id)])
        if hotel_ratings:
            cleanliness = sum(hotel_ratings.mapped('cleanliness')) / len(hotel_ratings.mapped('cleanliness'))
            comfort = sum(hotel_ratings.mapped('comfort')) / len(hotel_ratings.mapped('comfort'))
            staff = sum(hotel_ratings.mapped('staff')) / len(hotel_ratings.mapped('staff'))
            facilities_and_services = sum(hotel_ratings.mapped('facilities_and_services')) / len(hotel_ratings.mapped('facilities_and_services'))
            total_rate = sum(hotel_ratings.mapped('total_rate')) / len(hotel_ratings.mapped('total_rate'))
            comments = [{
                'partner_name': rating.partner_id.name,
                'description': rating.description,
                'create_date': rating.create_date.date().strftime('%d/%m/%Y'),
                'total_rate': rating.total_rate
            } for rating in hotel_ratings]
            values.update({
                'cleanliness': cleanliness,
                'comfort': comfort,
                'staff': staff,
                'facilities_and_services': facilities_and_services,
                'total_rate': total_rate,
                'comments': comments
            })

        reservation_lines = request.env['hotel.reservation.line'].sudo().search([
            ('line_id.shop_id', '=', kwargs['id']),
            ('line_id.state', '=', 'confirm'),
            ('checkin', '<=', datetime.now()),
            ('checkout', '>=', datetime.now())
        ])
        reserved_products = reservation_lines.mapped('room_number')
        limit = 2
        page = int(kwargs['page'] if kwargs.get('page') else 1)
        offset = (limit * page) - limit
        available_rooms = request.env['hotel.room'].sudo().search([
            ('product_id', 'not in', reserved_products.ids),
            ('shop_id', '=', kwargs['id'])
        ], offset=offset, limit=limit)
        if available_rooms:
            values['available_rooms'] = [{
                'id': room.id,
                'name': room.name,
                'brief': room.brief,
                'unit_price': room.list_price,
                'description': room.description_sale or '',
                'amenities': [{
                    'name': amenity.name,
                    'icon': amenity.icon_code
                } for amenity in room.room_amenities],
                'image_urls': [f'/web/image/hotel.room.image/{image.id}/image' for image in available_rooms.image_ids]
            } for room in available_rooms]
        available_rooms_count = request.env['hotel.room'].sudo().search_count([
            ('product_id', 'not in', reserved_products.ids),
            ('shop_id', '=', kwargs['id'])
        ])
        number_of_pages = math.ceil(available_rooms_count / limit)
        values['number_of_pages'] = number_of_pages
        values['page'] = page

        return request.render('iroom_website.hotel_page_template', values)

    @http.route('/api/check_reservation', methods=['POST', 'GET'], type='json', website=True, auth='public')
    def check_reservation(self, **kwargs):
        product = request.env['product.product'].sudo().browse(kwargs['room_id'])
        check_in = datetime.strptime(kwargs['check_in'], '%m/%d/%Y')
        check_out = datetime.strptime(kwargs['check_out'], '%m/%d/%Y')
        today = datetime.now().date()
        if check_in.date() < today or check_out.date() < today or check_in > check_out:
            return {
                'error': True,
                'message': _(f'You need to edit inserted dates!')
            }
        check_in = pytz.timezone(request.env.user.tz or 'UTC').localize(check_in).astimezone(pytz.utc).replace(tzinfo=None)
        check_out = pytz.timezone(request.env.user.tz or 'UTC').localize(check_out).astimezone(pytz.utc).replace(tzinfo=None)
        reservation_lines = request.env['hotel.reservation.line'].sudo().search([
            ('room_number', '=', product.id),
            ('checkin', '<=', check_in), ('checkout', '>=', check_in),
            '|',
            ('checkout', '<=', check_out), ('checkin', '<=', check_out)
        ])
        if reservation_lines:
            return {
                'error': True,
                'message': _(f'This room is not available accoring to inserted date range!')
            }
        return True

    # @http.route('/create_reservation', methods=['POST', 'GET'], type='json', website=True)
    # def create_reservation(self, **kwargs):
    #     user = request.env.user
    #     room_type = request.env['hotel.room_type'].sudo().browse(kwargs['room_type_id'])
    #     products = request.env['product.product'].sudo().search([('categ_id', '=', room_type.cat_id.id)])
    #     check_in = datetime.strptime(kwargs['check_in'], '%m/%d/%Y')
    #     check_in = pytz.timezone(request.env.user.tz or 'UTC').localize(check_in).astimezone(pytz.utc).replace(tzinfo=None)
    #     check_out = datetime.strptime(kwargs['check_out'], '%m/%d/%Y')
    #     check_out = pytz.timezone(request.env.user.tz or 'UTC').localize(check_out).astimezone(pytz.utc).replace(tzinfo=None)
    #     if check_in < datetime.now() or check_out < datetime.now() or check_in > check_out:
    #         return {
    #             'error': True,
    #             'message': _(f'You need to edit inserted dates!')
    #         }
    #     room = self.get_available_room(products, room_type.cat_id, check_in, check_out)
    #     if not room:
    #         return {
    #             'error': True,
    #             'message': _(f'There\'s no available rooms for type {room_type.name} at inserted date range!')
    #         }
    #
    #     reservation = request.env['hotel.reservation'].sudo().create({
    #         'partner_id': user.partner_id.id,
    #         'pricelist_id': user.partner_id.property_product_pricelist.id or 1,
    #         'shop_id': room_type.shop_id.id,
    #         'adults': kwargs['adult_number'],
    #         'childs': kwargs['children_number'],
    #         'source': 'through_web',
    #         'reservation_line': [(0, 0, {
    #             'checkin': check_in,
    #             'checkout': check_out,
    #             'categ_id': room_type.cat_id.id,
    #             'room_number': room.id,
    #             'price': room_type.unit_price
    #         })]
    #     })
    #     order = request.env['sale.order'].sudo().create({
    #         'partner_id': user.partner_id.id,
    #         'shop_id': room_type.shop_id.id,
    #         'website_id': request.website.id,
    #         'order_line': [(0, 0, {
    #             'product_id': room.id,
    #             'name': room.display_name,
    #             'product_uom_qty': 1,
    #             'price_unit': room_type.unit_price
    #         })]
    #     })
    #     order.action_confirm()
    #     reservation.order_id = order.id
    #     return {
    #         'success': True,
    #         'redirect_to': f'/my/orders/{order.id}'
    #     }
    #
    # def get_available_room(self, products, category, check_in, check_out):
    #     reservation_lines = request.env['hotel.reservation.line'].sudo().search([
    #         ('room_number', 'in', products.ids),
    #         ('checkin', '<=', check_in),
    #         ('checkout', '>=', check_out)
    #     ])
    #     reserved_rooms = reservation_lines.mapped('room_number')
    #     room = request.env['product.product'].sudo().search([
    #         ('id', 'not in', reserved_rooms.ids),
    #         ('categ_id', '=', category.id)
    #     ])
    #     return room[0] if room else None

    @http.route('/create_rating', methods=['POST', 'GET'], type='json', website=True)
    def create_rating(self, **kwargs):
        reservation_lines = request.env['hotel.reservation.line'].sudo().search([
            ('line_id.partner_id', '=', request.env.user.partner_id.id),
            ('line_id.state', '=', 'confirm'),
            ('checkin', '<=', datetime.now())
        ])
        reservations = reservation_lines.mapped('line_id')
        already_rated = request.env['hotel.reservation.rating'].sudo().search([('reservation_id', 'in', reservations.ids)])
        reservation_already_rated = already_rated.mapped('reservation_id')
        reservation_not_rated = reservations.filtered(lambda r: r.id not in reservation_already_rated .ids)
        request.env['hotel.reservation.rating'].sudo().create({
            'reservation_id': reservation_not_rated[0].id,
            'name': kwargs['name'],
            'email': kwargs['email'],
            'cleanliness': kwargs['cleanliness'],
            'comfort': kwargs['comfort'],
            'staff': kwargs['staff'],
            'facilities_and_services': kwargs['facilities_and_services'],
            'description': kwargs['description'],
        })
        return True
