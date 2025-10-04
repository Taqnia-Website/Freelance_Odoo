from odoo import models, fields


class SaleShopActivityLine(models.Model):
    _name = 'sale.shop.activity.line'

    name = fields.Char(required=True, translate=True)
    distance = fields.Float()
    description = fields.Text(required=True, translate=True)
    image = fields.Image()

    shop_id = fields.Many2one('sale.shop', 'Hotel', ondelete='CASCADE')
