import json
import requests
from requests.auth import HTTPBasicAuth
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    apply_ntmp = fields.Boolean(string='Apply NTMP', related='company_id.apply_ntmp', store=True)
    nationality_id = fields.Many2one('ntmp.nationality')
    gender_id = fields.Many2one('ntmp.gender', related='partner_id.gender_id')
    customer_type_id = fields.Many2one('ntmp.customer.type', related='partner_id.customer_type_id')
    visit_purpose_id = fields.Many2one('ntmp.visit.purpose', string='Purpose of Visit',
                                       related='partner_id.visit_purpose_id')
    payment_type_id = fields.Many2one('ntmp.payment.type')

    def done(self):
        res = super(HotelReservation, self).done()
        if self.apply_ntmp:
            for line in self.reservation_line:
                line.ntmp_connect(mode='check_in', new=False)
            days = self.get_reservation_days()
            for day in days:
                self.ntmp_update_occupancy(day)

        return res

    def confirmed_reservation(self):
        res = super().confirmed_reservation()
        days = self.get_reservation_days()
        for day in days:
            self.ntmp_update_occupancy(day)
        return res

    def cancel_reservation(self):
        transactions = self.reservation_line.mapped('ntmp_transaction_id')
        ignore_ntmp = self.env.context.get('ignore_ntmp', False)
        if (self.apply_ntmp and transactions) and not ignore_ntmp:
            return {
                'type': 'ir.actions.act_window',
                'name': "Cancel Reservation",
                'res_model': 'reservation.cancel',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_reservation_id': self.id,
                }
            }
        return super(HotelReservation, self).cancel_reservation()

    def ntmp_update_occupancy(self, day):
        occupied = len(self.get_occupied_rooms(day))
        booked = len(self.get_booked_rooms(day))
        on_maintenance = len(self.get_on_maintenance_rooms(day))
        total = len(self.get_total_rooms())
        available = total - occupied - booked - on_maintenance
        url = "https://dev-api.ntmp.gov.sa/gateway/OccupancyUpdate/2.0/occupancyUpdate"
        headers = self.prepare_ntmp_headers()
        data = {
            "updateDate": day.strftime('%Y%m%d'),
            "roomsOccupied": str(occupied),
            "roomsAvailable": str(available),
            "roomsBooked": str(booked),
            "roomsOnMaintenance": str(on_maintenance),
            "channel": self.company_id.ntmp_channel if self.company_id.ntmp_channel else "",
            # "transactionId": "Valid transaction Id from MT database",
            # "dayClosing": "false",
            "totalRooms": str(total),
            # "totalAdults": "10",
            # "totalChildren": "10",
            # "totalGuests": "20",
            # "totalRevenue": "2367"
        }
        response = requests.post(url=url, headers=headers, json=data, auth=HTTPBasicAuth(self.company_id.ntmp_username, self.company_id.ntmp_password))
        txt = json.loads(response.text)
        if txt.get('errorCode', False):
            error_code = txt['errorCode'][0]
            if error_code == '0':
                msg = "Occupancy Synced Successfully with NTMP"
            else:
                msg = self.get_response_msg(error_code)
            self.message_post(body=f"{response.text}, {msg}")


    def get_occupied_rooms(self, day):
        lines = self.env['hotel.reservation.line'].search([
            ('ntmp_transaction_id', '!=', False), ('line_id.state', '=', 'done')
        ]).filtered(
            lambda l: (l.checkin.date() <= day < l.checkout.date()) or (l.checkin.date() <= day < l.checkout.date()) or (l.checkin.date() <= day < l.checkout.date())
        )
        return lines

    def get_booked_rooms(self, day):
        lines = self.env['hotel.reservation.line'].search([
            ('ntmp_transaction_id', '!=', False), ('line_id.state', '=', 'confirm')
        ]).filtered(
            lambda l: (l.checkin.date() <= day < l.checkout.date()) or (l.checkin.date() <= day < l.checkout.date()) or (
                        l.checkin.date() <= day < l.checkout.date())
        )
        return lines

    def get_on_maintenance_rooms(self, day):
        rooms = self.env['rr.housekeeping'].search([
            ('date', '=', day), ('state', '!=', 'draft')
        ])
        return rooms

    def get_total_rooms(self):
        rooms = self.env['hotel.room'].search([('shop_id', '=', self.shop_id.id)])
        return rooms

    def prepare_ntmp_headers(self):
        return {
            "Content-Type": "application/json",
            "x-Gateway-APIKey": self.company_id.ntmp_key or "",
        }

    def get_response_msg(self, code):
        msg = False
        if code:
            response = self.env['ntmp.response.code'].search([
                ('api_name', '=', 'createOrUpdateBooking'), ('error_code', '=', code)
            ], limit=1)
            if response:
                if response.category == 'success':
                    msg = 'Synced Successfully with NTMP'
                else:
                    msg = response.error_description
        return msg

    def get_reservation_days(self):
        days = []
        for line in self.reservation_line:
            date_start = line.checkin.date()
            date_end = line.checkout.date()
            while date_start < date_end:
                days.append(date_start)
                date_start += relativedelta(days=1)
        return list(set(days))


class HotelReservationLine(models.Model):
    _inherit = 'hotel.reservation.line'

    rent_type_id = fields.Many2one('ntmp.rent.type', string='Room Rent Type')
    ntmp_room_type_id = fields.Many2one('ntmp.room.type', compute='compute_ntmp_room_type_id', store=True,
                                        string='NTMP Room Type')
    message = fields.Text()
    ntmp_transaction_id = fields.Char(string='NTMP Transaction ID')
    ntmp_msg_transaction_id = fields.Char(string='NTMP Message Transaction ID')

    @api.depends('categ_id')
    def compute_ntmp_room_type_id(self):
        for rec in self:
            rec.ntmp_room_type_id = False
            if rec.categ_id:
                room_type = self.env['hotel.room_type'].search([('cat_id', '=', rec.categ_id.id)])
                if room_type:
                    if room_type.ntmp_room_type_id:
                        rec.ntmp_room_type_id = room_type.ntmp_room_type_id.id

    @api.model
    def create(self, vals):
        res = super(HotelReservationLine, self).create(vals)
        if res.line_id.apply_ntmp:
            res.ntmp_connect(mode='booking', new=True)
        return res

    def write(self, vals):
        res = super(HotelReservationLine, self).write(vals)
        if self.line_id.apply_ntmp:
            if vals.get('price', False):
                self.ntmp_connect(mode='booking', new=False)
        return res

    def ntmp_connect(self, mode, new=False):
        # url = "https://api.ntmp.gov.sa/gateway/CreateOrUpdateBooking/1.0/createOrUpdateBooking"
        url = "https://dev-api.ntmp.gov.sa/gateway/CreateOrUpdateBooking/1.0/createOrUpdateBooking"
        headers = self.line_id.prepare_ntmp_headers()
        data = self.prepare_ntmp_data(mode=mode, new=new)
        response = requests.post(url=url, headers=headers, json=data, auth=HTTPBasicAuth(self.company_id.ntmp_username, self.company_id.ntmp_password))
        txt = json.loads(response.text)
        if new:
            self.ntmp_transaction_id = txt.get('transactionId', False)
        self.ntmp_msg_transaction_id = txt.get('transactionId', False)

        if txt.get('errorCode', False):
            error_code = txt['errorCode'][0]
            self.message = self.line_id.get_response_msg(error_code)

    def prepare_ntmp_data(self, mode, new=False):
        if self.number_of_days > 0:
            daily_room_rate = str(round((self.sub_total1 / self.number_of_days), 2))
        else:
            daily_room_rate = "0"
        if mode == 'booking':
            trx_type = "1"
        elif mode == 'check_in':
            trx_type = "2"
        else:
            trx_type = "3"
        reservation = self.line_id
        return {
            "channel": self.company_id.ntmp_channel if self.company_id.ntmp_channel else "",
            "bookingNo": str(self.id),
            "nationalityCode": reservation.nationality_id.code if reservation.nationality_id else "900",
            "checkInDate": self.checkin.strftime('%Y%m%d'),
            "checkOutDate": self.checkout.strftime('%Y%m%d'),
            "totalDurationDays": str(self.number_of_days),
            "allotedRoomNo": str(self.room_number.name) if self.room_number else "0",
            "roomRentType": self.rent_type_id.code if self.rent_type_id else "1",
            "dailyRoomRate": daily_room_rate,
            "totalRoomRate": str(self.sub_total1) if self.sub_total1 else "0",
            # "vat": str(round(self.price_vat, 2)) if self.price_vat else "0",
            # "municipalityTax": str(round(self.price_municipality, 2)) if self.price_municipality else "0",
            "vat": "0",
            "municipalityTax": "0",
            "discount": str(round(abs(self.discount), 2)) if self.discount else "0",
            "grandTotal": str(self.sub_total1) if self.sub_total1 else "0",
            "transactionTypeId": trx_type,
            "gender": reservation.partner_id.gender_id.code if reservation.partner_id.gender_id else "0",
            "transactionId": "" if new else self.ntmp_transaction_id,  # todo to be handled
            "checkInTime": "000000",  # todo to be handled
            "checkOutTime": "000000",  # todo to be handled
            "customerType": reservation.customer_type_id.code if reservation.customer_type_id else "3",
            "noOfGuest": "1",  # todo to be handled
            "roomType": self.ntmp_room_type_id.code if self.ntmp_room_type_id else "13",
            "purposeOfVisit": reservation.visit_purpose_id.code if reservation.visit_purpose_id else "7",
            "dateOfBirth": "0",  # todo to be handled
            "paymentType": "1",
            "noOfRooms": "1",
            "UserID": self.company_id.ntmp_username,
            "cuFlag": "1" if new else "2"
        }
