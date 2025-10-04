from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    is_supplier = fields.Boolean(string='Supplier')
