# -*- coding: utf-8 -*-

import math
import logging
from datetime import datetime, date
from odoo import models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    def _validate_reservation_dates_with_pricelist(self):
        """
        Ensure all reservation lines' check-in and check-out dates fall within the pricelist's date range.
        Raise UserError if not.
        """
        for reservation in self:
            pricelist = reservation.pricelist_id
            if not pricelist:
                continue
            # Get all pricelist items for this pricelist
            pricelist_items = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', pricelist.id)
            ])
            if not pricelist_items:
                continue  # No items, skip validation

            # Find the earliest start and latest end among all items
            date_start = min([item.date_start for item in pricelist_items if item.date_start] or [False])
            date_end = max([item.date_end for item in pricelist_items if item.date_end] or [False])

            # Convert pricelist dates to datetime for comparison
            if date_start:
                date_start = datetime.combine(date_start, datetime.min.time())
            if date_end:
                date_end = datetime.combine(date_end, datetime.min.time())

            for line in reservation.reservation_line:
                checkin = line.checkin
                checkout = line.checkout
                # Only validate if both dates are set
                if checkin and checkout:
                    # Ensure checkin and checkout are datetime objects
                    if isinstance(checkin, date):
                        checkin = datetime.combine(checkin, datetime.min.time())
                    if isinstance(checkout, date):
                        checkout = datetime.combine(checkout, datetime.min.time())

                    if date_start and checkin < date_start:
                        raise UserError(
                            "Reservation check-in date (%s) is before the pricelist's valid start date (%s)." %
                            (checkin.date(), date_start.date()))
                    if date_end and checkout > date_end:
                        raise UserError(
                            "Reservation check-out date (%s) is after the pricelist's valid end date (%s)." %
                            (checkout.date(), date_end.date()))

    def write(self, vals):
        """
        Override write method to include pricelist validation.
        """
        ret = super(HotelReservation, self).write(vals)
        self._validate_reservation_dates_with_pricelist()
        return ret

    @api.model_create_multi
    def create(self, vals):
        """
        Override create method to include pricelist validation.
        """
        res = super(HotelReservation, self).create(vals)
        res._validate_reservation_dates_with_pricelist()
        return res

    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        """
        Override the onchange_pricelist_id method to fix the issue where
        price lists are not automatically applied to future reservations.

        The fix ensures that when a pricelist is changed, the price calculation
        logic is executed first to handle future reservation dates properly.
        """
        self.show_update_pricelist = True

        # FIXED: Move the price calculation logic to the beginning
        # This ensures that future reservations get the correct pricing
        if 'checkin' in self._context and 'checkout' in self._context:
            room_obj = self.env['product.product']
            room_brw = room_obj.search(
                [('id', '=', self._context['hotel_resource'])])
            pricelist = self.env['sale.shop'].browse(
                int(self._context['shop_id'])).pricelist_id.id
            if pricelist == False:
                raise UserError(
                    ('Please set the Pricelist on the shop  %s to proceed further') % room_brw.shop_id.name)
            ctx = self._context and self._context.copy() or {}
            ctx.update({'date': self._context['checkin']})
            from dateutil import parser
            day_count1 = parser.isoparse(self._context['checkout']) - parser.isoparse(self._context['checkin'])

            day_count2 = day_count1.total_seconds()
            _logger.info("DIFF SECONDS===>>>>>>>>>{}".format(day_count2))
            day_count2 = day_count2 / 86400
            day_count2 = "{:.2f}".format(day_count2)
            day_count2 = math.ceil(float(day_count2))

            _logger.info("SELF CONTEXT====>>>>>{}".format(self._context['checkin']))
            res_line = {
                'categ_id': room_brw.categ_id.id,
                'room_number': room_brw.id,
                'checkin': parser.isoparse(self._context['checkin']),
                'checkout': parser.isoparse(self._context['checkout']),
                'number_of_days': int(day_count2),
                'price': self.env['product.pricelist'].with_context(ctx)._price_get(room_brw, 1)[pricelist]
            }
            if self.reservation_line:
                self.reservation_line.write(res_line)
            else:
                _logger.info("RES LINE===>>>>>>>>>>>>>>>{}".format(res_line))
                self.reservation_line = [[0, 0, res_line]]

        # Standard pricelist validation checks
        if not self.pricelist_id:
            return {}
        if not self.reservation_line:
            return {}
        if len(self.reservation_line) != 1:
            warning = {
                'title': _('Pricelist Warning!'),
                'message': _(
                    'If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
            }
            return {'warning': warning}


class HotelReservationLine(models.Model):
    _inherit = 'hotel.reservation.line'

    @api.onchange('room_number', 'checkin', 'checkout')
    @api.depends('checkin', 'checkout', 'banquet_id.pricelist_id', 'banquet_id', 'line_id.partner_id', 'number_of_days',
                 'banquet_id.source')
    def onchange_room_id(self):
        """
        Override the onchange_room_id method to fix the critical missing date parameter
        in the pricelist price calculation. This ensures that date-based pricing rules
        are properly applied when calculating room prices.

        The key fix is adding the 'date=self.checkin' parameter to the _price_get() method call.
        """
        v = {}
        warning = ''

        if self.room_number:
            product_browse = self.room_number
            product_id = product_browse.id
            price = product_browse.lst_price
            if price is False:
                raise ValidationError("Couldn't find a pricelist line matching this product!")
            pricelist = self.line_id.pricelist_id.id

            ctx = self._context and self._context.copy() or {}
            ctx.update({'date': self.checkin})

            if pricelist:
                # FIXED: Added the critical 'date=self.checkin' parameter
                # This ensures that pricelist calculations use the correct check-in date
                # for date-based pricing rules
                price = self.env['product.pricelist'].with_context(ctx)._price_get(
                    self.room_number, self.number_of_days, date=self.checkin)[pricelist]

            v['price'] = price
            tax_ids = []
            for tax_line in product_browse.taxes_id:
                tax_ids.append(tax_line.id)
            v['taxes_id'] = [(6, 0, tax_ids)]
            v['checkin'] = self.checkin
            v['checkout'] = self.checkout

            reservation_start_date = self.checkin
            reservation_end_date = self.checkout

            # GDS reservation conflict checking
            check_config = self.env['ir.model'].sudo().search([('model', '=', 'hotel.reservation.through.gds.configuration')])
            if check_config:
                config_id = self.env['hotel.reservation.through.gds.configuration'].search([])
                config_browse = config_id
                if config_browse and self.line_id.source != 'through_gds':
                    for record in config_browse:
                        config_start_date = record.name
                        config_end_date = record.to_date
                        config_start_date = datetime.strptime(str(config_start_date), '%Y-%m-%d %H:%M:%S')
                        config_end_date = datetime.strptime(str(config_end_date), '%Y-%m-%d %H:%M:%S')

                        if (config_start_date <= reservation_start_date < config_end_date) or (
                                config_start_date < reservation_end_date <= config_end_date) or (
                                (reservation_start_date < config_start_date) and (
                                reservation_end_date > config_end_date)):
                            for line in record.line_ids:
                                room_list = []
                                for room in line.room_number:
                                    room_list.append(room.id)
                                if self.room_number.id in room_list:
                                    raise UserError("Room  is reserved in this period for GDS reservation!")

            room_line_id = self.env['hotel.room'].search([('product_id', '=', product_id)])

            # Room housekeeping state validation
            housekeeping_room = self.env['hotel.housekeeping'].search([('room_no', '=', room_line_id.product_id.id)])
            if housekeeping_room:
                for house1 in housekeeping_room:
                    house = house1
                    house_current_date = house.current_date
                    house_current_date = datetime.strptime(str(house_current_date), '%Y-%m-%d %H:%M:%S')
                    house_end_date = house.end_date
                    house_end_date = datetime.strptime(str(house_end_date), '%Y-%m-%d %H:%M:%S')
                    start_reser = self.checkin
                    end_reser = self.checkout

                    if (((start_reser < house_current_date) and (end_reser > house_end_date)) or (
                            house_current_date <= start_reser < house_end_date) or (
                                house_current_date < end_reser <= house_end_date)) and (house.state == 'dirty'):
                        raise UserError("Warning! Room  %s is not clean for reservation period !" % (room_line_id.name))

            # Room booking history conflict detection
            if room_line_id.room_folio_ids:
                for history in room_line_id.room_folio_ids:
                    if history.state == 'done':
                        history_start_date = history.check_in
                        history_end_date = history.check_out

                        room_line_id = self.env['hotel.room'].search([('product_id', '=', product_id)])
                        housekeeping_room = self.env['hotel.housekeeping'].search([
                            ('room_no', '=', room_line_id.product_id.id), ('state', '=', 'dirty')])
                        if housekeeping_room:
                            for house1 in housekeeping_room:
                                house = house1
                                house_current_date = (
                                    datetime.strptime(str(house.current_date), '%Y-%m-%d %H:%M:%S')).date()
                                house_end_date = (datetime.strptime(str(house.end_date), '%Y-%m-%d %H:%M:%S')).date()
                                start_reser = datetime.strptime(str(self.checkin), '%Y-%m-%d %H:%M:%S').date()
                                end_reser = datetime.strptime(str(self.checkout), '%Y-%m-%d %H:%M:%S').date()
                                if (house_current_date <= start_reser <= house_end_date) or (
                                        house_current_date <= end_reser <= house_end_date) or (
                                        (start_reser < house_current_date) and (end_reser > house_end_date)):
                                    raise UserError("Room  %s is not clean for reservation period !" % (
                                        room_line_id.name))

                        # Agent booking logic handling
                        if (history_start_date <= reservation_start_date < history_end_date) or (
                                history_start_date < reservation_end_date <= history_end_date) or (
                                (reservation_start_date < history_start_date) and (
                                reservation_end_date > history_end_date)):
                            if not (self.line_id.id == history.booking_id.id):
                                if not self.line_id.agent_id_boolean == True:
                                    raise UserError(
                                        "Room  %s is booked in this reservation period !" % (room_line_id.name))
        return {'value': v, 'warning': warning}

