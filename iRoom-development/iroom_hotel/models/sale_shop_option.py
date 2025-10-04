from odoo import models, fields


class SaleShopOption(models.Model):
    _name = 'sale.shop.option'

    name = fields.Char(translate=True)

    sale_shop_id = fields.Many2one('sale.shop', 'Hotel', ondelete='CASCADE')
