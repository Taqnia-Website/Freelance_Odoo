from odoo import fields, models, api


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    @api.model
    def create(self, vals):
        shop_id = super(SaleShop, self).create(vals)
        self.env['ir.sequence'].create({
            'name': 'Hotel Reservations',
            'code': 'hotel.reservation',
            'prefix': 'HR/',
            'padding': 5,
            'company_id': shop_id.company_id.id,
        })
        return shop_id
