from odoo import models, fields


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    order_id = fields.Many2one('sale.order')
