from odoo import fields, models, api


class HotelLaundry(models.Model):
    _inherit = 'hotel.laundry'

    partner_id = fields.Many2one('res.partner', domain="[('is_supplier', '=', True)]")
