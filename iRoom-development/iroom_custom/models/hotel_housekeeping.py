from odoo import fields, models, api


class HotelHousekeeping(models.Model):
    _inherit = 'hotel.housekeeping'

    def room_clean(self):
        res = super(HotelHousekeeping, self).room_clean()
        if self.clean_type == 'checkout':
            room_id = self.env['hotel.room'].search([('product_id', '=', self.room_no.id)])
            if room_id:
                room_id.room_state = 'cleaning'
        return res


    def room_done(self):
        res = super(HotelHousekeeping, self).room_done()
        if self.clean_type == 'checkout':
            room_id = self.env['hotel.room'].search([('product_id', '=', self.room_no.id)])
            if room_id:
                room_id.room_state = 'vacant'
        return res


class RRHousekeeping(models.Model):
    _inherit = 'rr.housekeeping'

    def confirm_request(self):
        res = super(RRHousekeeping, self).confirm_request()
        self.room_no.room_state = 'maintenance'
        return res

    def done_task(self):
        res = super(RRHousekeeping, self).done_task()
        self.room_no.room_state = 'vacant'
        return res


class RRHousekeepingLine(models.Model):
    _inherit = 'rr.housekeeping.line'

    product_id = fields.Many2one('product.product', domain="[('repair_product', '=', True)]")
