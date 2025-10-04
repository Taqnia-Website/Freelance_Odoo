import json
import requests
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
import pytz
from odoo.exceptions import ValidationError


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    rate_plan_id = fields.Many2one('product.pricelist')
    apply_channex = fields.Boolean(related='shop_id.apply_channex', store=True)
    channex_id = fields.Char(string='Channex ID')
    channex_transaction_id = fields.Char(string='Revision ID')
    channex_channel_id = fields.Char(string='Channel ID')
    channex_unique_id = fields.Char(string='Unique ID')
    channex_acknowledge_status = fields.Char()
    channex_ota_name = fields.Char()
    channex_ota_commission = fields.Char()
    channex_ota_reservation_code = fields.Char()
    channex_payment_type = fields.Char()
    channex_agent = fields.Char()
    channex_card_number = fields.Char()
    channex_card_type = fields.Char()
    channex_cardholder_name = fields.Char()
    channex_card_expiration_date = fields.Char()
    channex_card_is_virtual = fields.Boolean()

    def done(self):
        res = super(HotelReservation, self).done()
        self.channex_update_availability()
        return res

    def confirmed_reservation(self):
        res = super().confirmed_reservation()
        self.channex_update_availability()
        return res

    def cancel_reservation(self):
        res = super(HotelReservation, self).cancel_reservation()
        self.channex_update_availability()
        return res

    def channex_update_availability(self):
        if self.shop_id.channex_id:
            url = f"{self.company_id.channex_url}/availability/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            timezone = pytz.timezone(self.env.user.tz or 'UTC')
            vals_lst = []
            for line in self.reservation_line:
                room_type = self.env['hotel.room_type'].search([('cat_id', '=', line.categ_id.id)])
                room_type_line = room_type.channex_ids.filtered(lambda l: l.shop_id.id == self.shop_id.id)
                if not room_type_line:
                    raise ValidationError(
                        f"There is no Channex ID for room type {line.categ_id.name} matching selected shop!")
                days = self.channex_get_reservation_days()
                for day in days:
                    confirmed = len(self.env['hotel.reservation.line'].search([
                        ('line_id.state', '=', 'confirm'), ('categ_id', '=', line.categ_id.id)
                    ]).filtered(
                        lambda l: (pytz.utc.localize(l.checkin).astimezone(timezone).date() <= day < pytz.utc.localize(l.checkout).astimezone(timezone).date())
                    ))
                    occupied = len(self.env['hotel_folio.line'].search([
                        ('folio_id.state', 'in', ['draft', 'sent', 'sale', 'progress']), ('categ_id', '=', line.categ_id.id)
                    ]).filtered(
                        lambda l: (pytz.utc.localize(l.checkin_date).astimezone(timezone).date() <= day < pytz.utc.localize(l.checkout_date).astimezone(timezone).date())
                    ))
                    on_maintenance = len(self.env['rr.housekeeping'].search([
                        ('state', '!=', 'draft'), ('room_no.categ_id', '=', line.categ_id.id)
                    ]).filtered(
                        lambda h: pytz.utc.localize(h.date).astimezone(timezone).date() == day
                    ))
                    total = self.env['hotel.room'].search_count([('categ_id', '=', line.categ_id.id)])
                    available = total - confirmed - occupied - on_maintenance
                    vals_lst.append({
                        "property_id": self.shop_id.channex_id,
                        "room_type_id": room_type_line.channex_id,
                        "date": day.strftime("%Y-%m-%d"),
                        "availability": available
                    })
            payload = json.dumps({
                "values": vals_lst
            })

            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)

    def channex_get_total_rooms(self):
        rooms = self.env['hotel.room'].search([('shop_id', '=', self.shop_id.id)])
        return rooms

    def channex_get_reservation_days(self):
        days = []
        for line in self.reservation_line:
            date_start = line.checkin.date()
            date_end = line.checkout.date()
            while date_start < date_end:
                days.append(date_start)
                date_start += relativedelta(days=1)
        return list(set(days))

    def get_channex_booking_revisions(self):
        shops = self.env['sale.shop'].search([('channex_id', '!=', False)])
        if shops:
            company = shops[0].company_id
            url = f"{company.channex_url}/booking_revisions/feed"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": company.channex_key
            }
            params = {
                "pagination[limit]": 20
            }
            response = requests.request("GET", url, headers=headers, params=params)
            reservations = json.loads(response.text).get('data', False)
            for reservation in reservations:
                data = reservation['attributes']
                reservation_id = self.env['hotel.reservation'].search([('channex_id', '=', data['booking_id'])])
                if reservation_id:
                    reservation_vals = {
                        'channex_acknowledge_status': data['acknowledge_status'],
                        'channex_agent': data['agent'],
                        'channex_id': data['booking_id'],
                        'channex_channel_id': data['channel_id'],
                        'channex_transaction_id': data['id'],
                        'note': data['notes'],
                        'channex_ota_name': data['ota_name'],
                        'channex_ota_commission': data['ota_commission'],
                        'channex_ota_reservation_code': data['ota_reservation_code'],
                        'channex_payment_type': data['payment_type'],
                    }
                    reservation_id.reservation_line = [(5, 0, 0)]
                    line_vals = []
                    lines = data['rooms']
                    for line in lines:
                        room_type_line = self.env['hotel.room_type.channex'].search([
                            ('shop_id', '=', reservation_id.shop_id.id), ('channex_id', '=', line['room_type_id'])
                        ])
                        if room_type_line:
                            line_vals.append([0, 0, {
                                'checkin': line['checkin_date'],
                                'checkout': line['checkout_date'],
                                'categ_id': room_type_line.room_type_id.cat_id.id,
                                'company_id': reservation_id.shop_id.company_id.id,
                                'price': line['amount'],
                            }])
                    if line_vals:
                        reservation_vals.update({'reservation_line': line_vals})
                    reservation_id.write(reservation_vals)
                    reservation_id.acknowledge_booking(data['id'])
                else:
                    customer_data = data['customer']
                    if customer_data.get('country', False):
                        country_id = self.env['res.country'].search([('code', '=', customer_data['country'])]).id
                    else:
                        country_id = False
                    customer_vals = {
                        'name': f"{customer_data['name']} {customer_data['surname']}",
                        'email': customer_data.get('mail', False),
                        'phone': customer_data.get('phone', False),
                        'mobile': customer_data.get('phone'),
                        'street': customer_data.get('address'),
                        'city': customer_data.get('city', False),
                        'country_id': country_id,
                        'zip': customer_data.get('zip', False)
                    }
                    customer = self.env['res.partner'].create(customer_vals)
                    shop_id = self.env['sale.shop'].search([('channex_id', '=', data['property_id'])])
                    reservation_vals = {
                        'partner_id': customer.id,
                        'shop_id': shop_id.id,
                        'pricelist_id': self.env['product.pricelist'].search([], limit=1).id,
                        'company_id': shop_id.company_id.id,
                        'channex_acknowledge_status': data['acknowledge_status'],
                        'channex_agent': data['agent'],
                        'channex_id': data['booking_id'],
                        'channex_channel_id': data['channel_id'],
                        'channex_transaction_id': data['id'],
                        'note': data['notes'],
                        'channex_ota_name': data['ota_name'],
                        'channex_ota_commission': data['ota_commission'],
                        'channex_ota_reservation_code': data['ota_reservation_code'],
                        'channex_payment_type': data['payment_type'],
                    }
                    line_vals = []
                    lines = data['rooms']
                    for line in lines:
                        room_type_line = self.env['hotel.room_type.channex'].search([
                            ('shop_id', '=', shop_id.id), ('channex_id', '=', line['room_type_id'])
                        ])
                        if room_type_line:
                            line_vals.append([0, 0, {
                                'checkin': line['checkin_date'],
                                'checkout': line['checkout_date'],
                                'categ_id': room_type_line.room_type_id.cat_id.id,
                                'company_id': shop_id.company_id.id,
                                'price': line['amount'],
                            }])
                    if line_vals:
                        reservation_id = self.env['hotel.reservation'].create(reservation_vals)
                        reservation_id.write({
                            'reservation_line': line_vals
                        })
                        reservation_id.acknowledge_booking(data['id'])
                        reservation_id.confirmed_reservation()

    def acknowledge_booking(self, revision_id):
        url = f"{self.company_id.channex_url}/booking_revisions/{revision_id}/ack"
        headers = {
            "Content-Type": "application/json",
            "user-api-key": self.company_id.channex_key
        }
        response = requests.request("POST", url, headers=headers)
        if response.status_code == 200:
            self.message_post(body="Booking acknowledged successfully")
        else:
            self.message_post(body="Booking can't be acknowledged!")


class HotelReservationLine(models.Model):
    _inherit = 'hotel.reservation.line'

    room_number = fields.Many2one('product.product', required=False)
