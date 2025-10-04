from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    repair_product = fields.Boolean(string='Repair')
