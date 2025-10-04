import base64
import imghdr

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
import json
from datetime import datetime, date
from collections import defaultdict


class HotelWebsite(http.Controller):

    @http.route(['/single-hotel'], type='http', auth="public", website=True)
    def single_hotel(self, **kw):
        data = kw
        hotel_select = int(kw.get('hotel_select', 0))
        from_date = kw.get('from_date', False)
        to_date = kw.get('to_date', False)
        available_rooms = defaultdict(list)

        vacant_rooms = request.env['hotel.room'].sudo().search([
            ('room_state', '=', 'vacant'), ('shop_id', '=', hotel_select)
        ])
        room_categories = vacant_rooms.mapped('categ_id')
        for category in room_categories:
            category_rooms = vacant_rooms.filtered(lambda r: r.categ_id == category)
            for room in category_rooms:
                bookings = request.env['hotel.room.booking.history'].sudo().search([
                    ('history_id', '=', room.id),
                    '&', ('check_in', '>=', from_date), ('check_in', '<=', to_date),
                    '&', ('check_out', '>=', from_date), ('check_out', '<=', to_date),
                ])
                draft_reservation_lines = request.env['hotel.reservation.line'].sudo().search([
                    ('line_id.state', '!=', 'cancel'),
                    ('room_number', 'in', room.product_id.ids),
                    '|',
                    '&', ('checkin', '>=', from_date), ('checkin', '<=', to_date),
                    '&', ('checkout', '>=', from_date), ('checkout', '<=', to_date),
                ])

                if not bookings and not draft_reservation_lines:
                    available_rooms[category].append(room)

        return request.render('iroom_website.website_single_hotel', {
            'hotel_available_rooms': available_rooms,
            'hotel': request.env['sale.shop'].search([('id', '=', hotel_select)]),
            'from_date': from_date,
            'to_date': to_date,
        })

    @http.route('/get_hotel_data', type='json', auth='public', methods=['POST'], website=True)
    def get_hotel_data(self, hotel_id):
        def encode_image(image):
            if not image:
                return '/web/static/img/placeholder.png'  # Default Odoo placeholder image
            try:
                # Image is already base64-encoded in Odoo Binary fields
                image_data = base64.b64decode(image)
                image_format = imghdr.what(None, h=image_data)
                mime_type = f"image/{image_format}" if image_format else 'image/png'
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                return f"data:{mime_type};base64,{image_base64}"
            except Exception as e:
                return '/web/static/img/placeholder.png'

        try:
            hotel = request.env['sale.shop'].sudo().browse(int(hotel_id))
            room_category = request.env['hotel.room_type'].sudo().search([])
            # hotel fallback & data passing
            if not hotel.exists():
                return {'error': 'Hotel not found'}

            # Prepare amenity data
            amenities_list = [
                {'id': amenity.id, 'name': amenity.name}
                for amenity in hotel.amenity_ids
            ]

            # Prepare image IDs with proper URL
            image_ids = [
                {'url': encode_image(img.image)}
                for img in hotel.image_ids
                if img.image
            ]

            # room category data passing
            room_image = room_category.img_ids

            hotel_data = {
                'id': hotel.id,
                'name': hotel.name,
                'description': hotel.description or 'لا يوجد وصف متاح',
                'location_iframe': hotel.location_iframe or '',
                'amenities': amenities_list,
                'image_ids': image_ids,
                'number_of_restaurants': hotel.number_of_restaurants or 0,
                'distance_from_center': hotel.distance_from_center or 0,
                'website': hotel.website or 0,
                'email': hotel.email or 0,
                'address': hotel.address or 0,
                'mobile': hotel.mobile or 0,
            }
            return hotel_data
        except Exception as e:
            return {'error': f'Error fetching hotel data: {str(e)}'}

    @http.route('/booking-process', type='http', auth='public', website=True)
    def booking_process(self, **kwargs):
        # Extract query parameters with defaults
        room_title = kwargs.get('room_title', 'غرفة ديلوكس توأم')
        adults = kwargs.get('adults', '2')
        children = kwargs.get('children', '0')
        from_date = kwargs.get('from_date', '2025-05-20')
        to_date = kwargs.get('to_date', '2025-05-21')
        room_price = kwargs.get('room_price', '200')
        number_of_rooms = kwargs.get('number_of_rooms', 1)

        # Validate numeric inputs
        try:
            adults = int(adults)
            children = int(children)
            room_price = float(room_price)
            number_of_rooms = int(kwargs.get('number_of_rooms', 1))  # FIXED
            if adults < 0 or children < 0 or room_price < 0 or number_of_rooms < 1:
                raise ValueError("Invalid values")
        except ValueError:
            adults = 2
            children = 0
            room_price = 200
            number_of_rooms = 1

        # Calculate number of days
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            days = (to_date_obj - from_date_obj).days
            if days <= 0:
                raise ValueError("Invalid date range")
        except ValueError:
            days = 3
            from_date = '2025-05-20'
            to_date = '2025-05-21'

        # Calculate fees and discount (example logic)
        fees = 12  # Replace with your logic
        discount = 10 if children > 0 else 0  # Example discount for children

        # Pass data to the template
        values = {
            'room_title': room_title,
            'adults': adults,
            'children': children,
            'from_date': from_date,
            'to_date': to_date,
            'days': days,
            'room_price': room_price,
            'number_of_rooms': number_of_rooms,
            'fees': fees,
            'discount': discount,
        }
        # Store in session
        request.session['booking_data'] = values

        if not request.env.user._is_public():
            values.update({
                'user_name': request.env.user.name.split(' ')[0],
                'user_lastname': request.env.user.name.split(' ')[-1],
                'user_email': request.env.user.email,
                'user_phone': request.env.user.phone,
            })
        # Render with same values
        return request.render('iroom_website.website_booking_process', values)

    @http.route('/get_room_images', type='json', auth='public', methods=['POST'])
    def get_room_images(self, **kwargs):
        room_type_id = kwargs.get('params', {}).get('room_type_id', 0)
        room_type = request.env['hotel.room_type'].sudo().browse(int(room_type_id))
        if not room_type.exists():
            return {'error': 'Room type not found'}
        image_ids = [
            {'id': img.id, 'img': bool(img.img)}
            for img in room_type.img_ids
        ]
        return {'result': {'image_ids': image_ids}}

    @http.route('/get_booking_details', type='json', auth='public', website=True, csrf=False)
    def get_booking_details(self, **kwargs):
        booking_data = request.session.get('booking_data')
        from_date = datetime.strptime(booking_data.get('from_date'), '%Y-%m-%d')
        to_date = datetime.strptime(booking_data.get('to_date'), '%Y-%m-%d')
        number_of_rooms = booking_data.get('number_of_rooms')

        try:
            data = json.loads(request.httprequest.get_data().decode('utf-8'))
            if not data:
                return {'success': False, 'message': 'No data received'}

            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            phone = data.get('phone')
            email = data.get('email')
            country_name = data.get('country')
            city = data.get('city')
            postal_code = data.get('postal_code')
            notes = data.get('notes')

            if not first_name or not last_name:
                return {'success': False, 'message': 'First and last name are required'}

            full_name = f"{first_name} {last_name}"

            # Find country
            country = request.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
            if not country:
                return {'success': False, 'message': f"Country '{country_name}' not found"}

            # Search or create partner
            Partner = request.env['res.partner'].sudo()
            partner = Partner.search([
                # ('name', '=', full_name),
                ('email', '=', email)
            ], limit=1)

            if partner:
                partner.write({
                    'name': full_name,
                    'phone': phone,
                    'country_id': country.id,
                    'city': city,
                    'zip': postal_code,
                    'comment': notes,
                })

            else:
                partner = Partner.sudo().create({
                    'name': full_name,
                    'phone': phone,
                    'email': email,
                    'country_id': country.id,
                    'city': city,
                    'zip': postal_code,
                    'comment': notes,
                })

            # Create reservation with one2many lines
            Reservation = request.env['hotel.reservation'].sudo()
            reservation = Reservation.sudo().create({
                'partner_id': partner.id,
                'date_order': date.today(),
                'pricelist_id': 1,
                'company_id': request.env.company.id,
                'note': notes,
            })

            room_type_id = request.env['hotel.room_type'].sudo().search(
                [('name', '=ilike', booking_data.get('room_title', ''))], limit=1)
            room_ids = request.env['hotel.room'].sudo().search([
                ('categ_id', '=', room_type_id.cat_id.id),
            ])
            room_history_ids = request.env['hotel.room.booking.history'].sudo().search([
                ('history_id', 'in', room_ids.ids),
                '|',
                '&', ('check_in', '>=', from_date), ('check_in', '<=', to_date),
                '&', ('check_out', '>=', from_date), ('check_out', '<=', to_date),
            ])
            draft_reservation_lines = request.env['hotel.reservation.line'].sudo().search([
                ('line_id.state', '!=', 'cancel'),
                ('room_number', 'in', room_ids.product_id.ids),
                '|',
                '&', ('checkin', '>=', from_date), ('checkin', '<=', to_date),
                '&', ('checkout', '>=', from_date), ('checkout', '<=', to_date),
            ])

            draft_rooms = room_ids.filtered(lambda r: r.product_id in draft_reservation_lines.room_number)

            available_rooms = room_ids - room_history_ids.history_id - draft_rooms
            # Create reservation lines (example data - you should pass your own values)
            if len(available_rooms) < number_of_rooms:
                raise ValidationError("There is no enough rooms")
            for i in range(number_of_rooms):
                reservation_line = request.env['hotel.reservation.line'].sudo().create({
                    'line_id': reservation.id,
                    'categ_id': room_type_id.cat_id.id,
                    'room_number': available_rooms[i].product_id.id,
                    'company_id': request.env.company.id,
                    'checkin': datetime.strptime(booking_data.get('from_date'), '%Y-%m-%d'),
                    'checkout': datetime.strptime(booking_data.get('to_date'), '%Y-%m-%d'),
                })
                values = reservation_line.onchange_room_id_test().get('value')
                reservation_line.write(values)

        except json.JSONDecodeError as e:
            return {'success': False, 'message': f'Invalid JSON: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Odoo Error: {str(e)}'}
