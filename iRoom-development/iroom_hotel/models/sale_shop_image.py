from odoo import models, fields


class SaleShopImage(models.Model):
    _name = 'sale.shop.image'

    image = fields.Image()

    sale_shop_id = fields.Many2one('sale.shop', 'Hotel', ondelete='CASCADE')