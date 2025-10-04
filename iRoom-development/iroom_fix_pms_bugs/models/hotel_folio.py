from odoo import exceptions, models, _


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    def action_checkout(self):
        for folio in self:
            if folio.remaining_amt != 0:
                raise exceptions.UserError(
                    _('Outstanding balance Pay now to checkout.'))
        
        return super().action_checkout()

