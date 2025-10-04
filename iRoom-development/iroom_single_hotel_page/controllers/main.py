import json
import math

from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
class HotelWebsite(http.Controller):

    @http.route('/hotel/<string:hotel_url_path>', type='http', auth="public", website=True)
    def single_hotel(self, hotel_url_path=None, **kwargs):
        hotel = request.env['sale.shop'].sudo().with_context(lang=request.context['lang']).search([('hotel_url_path', '=', hotel_url_path)])
        if not hotel:
            return request.redirect('/not_found')
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
                # 'can_rate': False
            }
        except Exception as e:
            return request.redirect('/not_found')

        rooms_count = request.env['hotel.room'].sudo().search_count([('shop_id', '=', hotel.id)])
        values['rooms_count'] = rooms_count

        if hotel.image_ids:
            values['image_urls_1_to_4'] = [f'/web/image/sale.shop.image/{image.id}/image' for image in hotel.image_ids[0:5]]
            if len(hotel.image_ids) > 4:
                values['image_url_5'] = f'/web/image/sale.shop.image/{hotel.image_ids[5].id}/image'
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

        # if hotel.similar_hotels_ids:
        #     values['similar_hotels'] = [{
        #         'name': similar.name,
        #         'url': f'/hotel/{similar.id}',
        #         'image_url': f'/web/image/sale.shop/{similar.id}/shop_img' or '',
        #         'close_to': similar.close_to
        #     } for similar in hotel.similar_hotels_ids]

        rooms = request.env['hotel.room'].sudo().with_context(lang=request.context['lang']).search([('shop_id', '=', hotel.id)])
        if rooms:
            values['rooms'] = [{
                'id': room.product_id.id,
                'name': room.name,
                'unit_price': room.list_price
            } for room in rooms]

        # if not request.env.user._is_public():
        #     reservation_lines = request.env['hotel.reservation.line'].sudo().search([
        #         ('line_id.partner_id', '=', request.env.user.partner_id.id),
        #         ('line_id.shop_id', '=', int(hotel.id)),
        #         ('line_id.state', '=', 'confirm'),
        #         ('checkin', '<=', datetime.now())
        #     ])
        #     reservation_ids = reservation_lines.mapped('line_id').ids
        #     if reservation_ids:
        #         ratings = request.env['hotel.reservation.rating'].sudo().search([('reservation_id', 'in', reservation_ids)])
        #         values['can_rate'] = True if not ratings else False
        # else:
        #     # Signup details
        #     countries = request.env['res.country'].sudo().with_context(lang=request.context['lang']).search([])
        #     values['countries'] = [{'id': country.id, 'name': country.name} for country in countries]
        #
        # hotel_ratings = request.env['hotel.reservation.rating'].sudo().search([('shop_id', '=', hotel.id)])
        # if hotel_ratings:
        #     cleanliness = sum(hotel_ratings.mapped('cleanliness')) / len(hotel_ratings.mapped('cleanliness'))
        #     comfort = sum(hotel_ratings.mapped('comfort')) / len(hotel_ratings.mapped('comfort'))
        #     staff = sum(hotel_ratings.mapped('staff')) / len(hotel_ratings.mapped('staff'))
        #     facilities_and_services = sum(hotel_ratings.mapped('facilities_and_services')) / len(hotel_ratings.mapped('facilities_and_services'))
        #     total_rate = sum(hotel_ratings.mapped('total_rate')) / len(hotel_ratings.mapped('total_rate'))
        #     comments = [{
        #         'partner_name': rating.partner_id.name,
        #         'description': rating.description,
        #         'create_date': rating.create_date.date().strftime('%d/%m/%Y'),
        #         'total_rate': rating.total_rate
        #     } for rating in hotel_ratings]
        #     values.update({
        #         'cleanliness': cleanliness,
        #         'comfort': comfort,
        #         'staff': staff,
        #         'facilities_and_services': facilities_and_services,
        #         'total_rate': total_rate,
        #         'comments': comments
        #     })

        # reservation_lines = request.env['hotel.reservation.line'].sudo().search([
        #     ('line_id.shop_id', '=', hotel.id),
        #     ('line_id.state', '=', 'confirm'),
        #     ('checkin', '<=', datetime.now()),
        #     ('checkout', '>=', datetime.now())
        # ])
        # reserved_products = reservation_lines.mapped('room_number')
        # limit = 2
        # page = int(kwargs['page'] if kwargs.get('page') else 1)
        # offset = (limit * page) - limit
        # available_rooms = request.env['hotel.room'].sudo().search([
        #     ('product_id', 'not in', reserved_products.ids),
        #     ('shop_id', '=', hotel.id)
        # ], offset=offset, limit=limit)

        # if available_rooms:
        #     values['available_rooms'] = [{
        #         'id': room.id,
        #         'name': room.name,
        #         'brief': room.brief,
        #         'unit_price': room.list_price,
        #         'description': room.description_sale or '',
        #         'amenities': [{
        #             'name': amenity.name,
        #             'icon': amenity.icon_code
        #         } for amenity in room.room_amenities],
        #         'image_urls': [f'/web/image/hotel.room.image/{image.id}/image' for image in available_rooms.image_ids]
        #     } for room in available_rooms]
        # available_rooms_count = request.env['hotel.room'].sudo().search_count([
        #     ('product_id', 'not in', reserved_products.ids),
        #     ('shop_id', '=', hotel.id)
        # ])
        # number_of_pages = math.ceil(available_rooms_count / limit)
        # values['number_of_pages'] = number_of_pages
        # values['page'] = page
        #
        # print('available_rooms:', values['available_rooms'])
        return request.render('iroom_single_hotel_page.single_hotel_page', values)