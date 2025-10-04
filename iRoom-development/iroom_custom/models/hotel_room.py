from odoo import fields, models, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
import pytz
import logging

_logger = logging.getLogger(__name__)

class HotelRoom(models.Model):
    _inherit = 'hotel.room'

    room_state = fields.Selection(selection=[
        ('vacant', 'Vacant'), ('booking', 'Booking'), ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'), ('checked_out', 'Checked Out'),
        ('cleaning', 'Under Cleaning'), ('maintenance', 'Under Maintenance')
    ], default='vacant')

    room_partner_id = fields.Many2one('res.partner', compute='compute_room_info')
    room_ref = fields.Char(compute='compute_room_info')
    room_check_in = fields.Char(compute='compute_room_info')
    room_check_in_time = fields.Char(compute='compute_room_info')
    room_check_out = fields.Char(compute='compute_room_info')
    room_check_out_time = fields.Char(compute='compute_room_info')
    room_total_nights = fields.Integer(compute='compute_room_info')
    room_booking_date = fields.Date(compute='compute_room_info')
    room_adults = fields.Integer(compute='compute_room_info')
    room_children = fields.Integer(compute='compute_room_info')
    room_total_price = fields.Float(compute='compute_room_info')

    room_amenities = fields.Many2many('hotel.room_amenities', 'temp_tab', 'room_amenities', 'rcateg_id', 'Room Amenities',
                                      domain="[('categ_id.isamenitype', '=', True)]")


    def compute_room_info(self):
        for rec in self:
            rec.room_partner_id = False
            rec.room_ref = False
            rec.room_check_in = False
            rec.room_check_in_time = False
            rec.room_check_out = False
            rec.room_check_out_time = False
            rec.room_total_nights = False
            rec.room_booking_date = False
            rec.room_adults = False
            rec.room_children = False
            rec.room_total_price = False


            folio_line = self.env['hotel_folio.line'].search([
                ('product_id', '=', rec.product_id.id), ('folio_id.state', 'not in', ['cancel', 'done'])
            ], limit=1)
            if folio_line:
                # user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                # print(user_tz)
                # date_today = pytz.utc.localize(folio_line.checkin_date).astimezone(user_tz)
                # print(date_today)
                # Get user time zone with fallback to UTC
                user_tz = self.env.context.get('tz') or self.env.user.tz or 'UTC'
                try:
                    user_tz = pytz.timezone(user_tz)
                except Exception as e:
                    _logger.warning("Invalid user timezone %s for user %s. Falling back to UTC.", user_tz,
                                    self.env.user.name)
                    user_tz = pytz.timezone('UTC')

                # Convert checkin_date and checkout_date to user time zone
                if folio_line.checkin_date:
                    checkin_utc = pytz.utc.localize(folio_line.checkin_date)
                    checkin_local = checkin_utc.astimezone(user_tz)
                    rec.room_check_in = checkin_local.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    rec.room_check_in_time = checkin_local.strftime('%I:%M:%S %p')
                    _logger.info("Room %s check-in: UTC %s -> Local %s (%s)", rec.name, folio_line.checkin_date,
                                 rec.room_check_in_time, user_tz.zone)
                else:
                    _logger.warning("No checkin_date for folio line %s", folio_line.id)

                if folio_line.checkout_date:
                    checkout_utc = pytz.utc.localize(folio_line.checkout_date)
                    checkout_local = checkout_utc.astimezone(user_tz)
                    rec.room_check_out = checkout_local.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    rec.room_check_out_time = checkout_local.strftime('%I:%M:%S %p')
                    _logger.info("Room %s check-out: UTC %s -> Local %s (%s)", rec.name, folio_line.checkout_date,
                                 rec.room_check_out_time, user_tz.zone)
                else:
                    _logger.warning("No checkout_date for folio line %s", folio_line.id)
                rec.room_partner_id = folio_line.folio_id.partner_id.id
                rec.room_ref = folio_line.folio_id.name
                rec.room_total_nights = int(folio_line.product_uom_qty)
                rec.room_booking_date = folio_line.folio_id.reservation_id.date_order
                rec.room_total_price = folio_line.price_total
                folio_reservation_line = folio_line.folio_id.reservation_id.reservation_line.filtered(lambda l: l.room_number.id == rec.product_id.id)
                if folio_reservation_line:
                    rec.room_adults = folio_reservation_line[0].adults
                    rec.room_children = folio_reservation_line[0].children
            else:
                reservation_line = self.env['hotel.reservation.line'].search([
                    ('room_number', '=', rec.product_id.id), ('line_id.state', '=', 'confirm'),
                ], limit=1)
                if not reservation_line:
                    reservation_line = self.env['hotel.reservation.line'].search([
                        ('room_number', '=', rec.product_id.id), ('line_id.state', '=', 'draft'),
                    ], limit=1)
                if reservation_line:
                    user_tz = self.env.context.get('tz') or self.env.user.tz or 'UTC'
                    try:
                        user_tz = pytz.timezone(user_tz)
                    except Exception as e:
                        _logger.warning("Invalid user timezone %s for user %s. Falling back to UTC.", user_tz,
                                        self.env.user.name)
                        user_tz = pytz.timezone('UTC')

                    if reservation_line.checkin:
                        checkin_utc = pytz.utc.localize(reservation_line.checkin)
                        checkin_local = checkin_utc.astimezone(user_tz)
                        rec.room_check_in = checkin_local.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        rec.room_check_in_time = checkin_local.strftime('%I:%M:%S %p')
                        _logger.info("Room %s check-in (reservation): UTC %s -> Local %s (%s)", rec.name,
                                     reservation_line.checkin, rec.room_check_in_time, user_tz.zone)
                    if reservation_line.checkout:
                        checkout_utc = pytz.utc.localize(reservation_line.checkout)
                        checkout_local = checkout_utc.astimezone(user_tz)
                        rec.room_check_out = checkout_local.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        rec.room_check_out_time = checkout_local.strftime('%I:%M:%S %p')
                        _logger.info("Room %s check-out (reservation): UTC %s -> Local %s (%s)", rec.name,
                                     reservation_line.checkout, rec.room_check_out_time, user_tz.zone)
                    rec.room_partner_id = reservation_line.line_id.partner_id.id
                    rec.room_ref = reservation_line.line_id.name
                    rec.room_total_nights = int(reservation_line.number_of_days)
                    rec.room_booking_date = reservation_line.line_id.date_order
                    rec.room_adults = reservation_line.adults
                    rec.room_children = reservation_line.children
                    rec.room_total_price = reservation_line.sub_total1


    def action_view_room_reservation(self):
        housekeeping = self.env['hotel.housekeeping'].search([
            ('room_no', '=', self.product_id.id), ('state', 'not in', ['cancel', 'done'])
        ], limit=1)
        if housekeeping:
            return {
                'name': _('Housekeeping'),
                'view_mode': 'form',
                'res_model': 'hotel.housekeeping',
                'res_id': housekeeping.id,
                'type': 'ir.actions.act_window',
            }
        folio_line = self.env['hotel_folio.line'].search([
            ('product_id', '=', self.product_id.id), ('folio_id.state', 'not in', ['cancel', 'done'])
        ], limit=1)
        if folio_line:
            return {
                'name': _('Folio'),
                'view_mode': 'form',
                'res_model': 'hotel.folio',
                'res_id': folio_line.folio_id.id,
                'type': 'ir.actions.act_window',
            }
        reservation_line = self.env['hotel.reservation.line'].search([
            ('room_number', '=', self.product_id.id), ('line_id.state', '=', 'confirm'),
        ], limit=1)
        if not reservation_line:
            reservation_line = self.env['hotel.reservation.line'].search([
                ('room_number', '=', self.product_id.id), ('line_id.state', '=', 'draft'),
            ], limit=1)
        action = {
            'name': _('Reservation'),
            'view_mode': 'form',
            'res_model': 'hotel.reservation',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if reservation_line:
            action.update({
                'res_id': reservation_line.line_id.id,
            })
        else:
            action.update({
                'context': {
                    'default_reservation_line': self.get_default_room_line(),
                }
            })
        return action

    def get_default_room_line(self):
        return [(0, 0,{
            'room_number': self.product_id.id,
            'company_id': self.env.company.id,
            'categ_id': self.categ_id.id,
            'checkin': datetime.now(),
            'checkout': datetime.now() + relativedelta(days=1),
            'price': self.list_price,
            'adults': self.product_id.max_adult or self.max_adult or self.room_adults,
            'children': self.product_id.max_child or self.max_child or self.room_children,
        })]

    def action_create_future_reservation(self):
        return {
            'name': _('Create Future Reservation'),
            'view_mode': 'form',
            'res_model': 'create.future.reservation',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_product_id': self.product_id.id
            }
        }
