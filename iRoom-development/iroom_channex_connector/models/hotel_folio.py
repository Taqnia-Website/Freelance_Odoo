from odoo import fields, models, api


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    def action_checkout(self):
        res = super(HotelFolio, self).action_checkout()
        if self.reservation_id:
            self.reservation_id.channex_update_availability()
        return res

    def action_cancel(self):
        res = super(HotelFolio, self).action_cancel()
        if self.reservation_id:
            self.reservation_id.channex_update_availability()
        return res