from odoo import models, fields


class SaleShopTag(models.Model):
    _name = 'sale.shop.tag'

    name = fields.Char('Tag')