from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class CreateFutureReservation(models.TransientModel):
    _name = 'create.future.reservation'
    _description = 'Create Future Reservation'

    product_id = fields.Many2one('product.product', string='Room Number', required=True)
    checkin = fields.Datetime(default=fields.Datetime.now, required=True)

    def button_create_future_reservation(self):
        self.can_reserve_room()
        return {
            'name': _('Reservation'),
            'view_mode': 'form',
            'res_model': 'hotel.reservation',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {
                'default_reservation_line': self.get_default_room_line(self.product_id)
            }
        }


    def can_reserve_room(self):
        reservation_start_date = self.checkin
        reservation_end_date = self.checkin + relativedelta(days=1)
        product_id = self.product_id.id

        room_line_id = self.env['hotel.room'].search([('product_id', '=', product_id)])

        housekeeping_room = self.env['hotel.housekeeping'].search([('room_no', '=', room_line_id.product_id.id)])
        if housekeeping_room:
            for house1 in housekeeping_room:
                house = house1
                house_current_date = house.current_date
                house_current_date = datetime.strptime(str(house_current_date), '%Y-%m-%d %H:%M:%S')

                house_end_date = house.end_date
                house_end_date = datetime.strptime(str(house_end_date), '%Y-%m-%d %H:%M:%S')

                start_reser = self.checkin
                end_reser = self.checkin + relativedelta(days=1)

                if (((start_reser < house_current_date) and (end_reser > house_end_date)) or (
                        house_current_date <= start_reser < house_end_date) or (
                            house_current_date < end_reser <= house_end_date)) and (house.state == 'dirty'):
                    raise UserError("Warning! Room  %s is not clean for reservation period !" % (room_line_id.name))

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
                            end_reser = datetime.strptime(str(self.checkin + relativedelta(days=1)), '%Y-%m-%d %H:%M:%S').date()
                            if (house_current_date <= start_reser <= house_end_date) or (
                                    house_current_date <= end_reser <= house_end_date) or (
                                    (start_reser < house_current_date) and (end_reser > house_end_date)):
                                raise UserError("Room  %s is not clean for reservation period !" % (
                                    room_line_id.name))

                    if (history_start_date <= reservation_start_date < history_end_date) or (
                            history_start_date < reservation_end_date <= history_end_date) or (
                            (reservation_start_date < history_start_date) and (
                            reservation_end_date > history_end_date)):
                        raise UserError("Room  %s is booked in this reservation period !" % (room_line_id.name))

    @api.model
    def get_default_room_line(self, product_id):
        return [(0, 0,
                 {
                     'room_number': product_id.id,
                     'categ_id': product_id.categ_id.id,
                     'checkin': self.checkin,
                     'checkout': self.checkin + relativedelta(days=1),
                     'price': product_id.list_price
                 }),
                ]
