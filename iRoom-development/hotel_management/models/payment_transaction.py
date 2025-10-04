from odoo import fields, models, api


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    reservation_id = fields.Many2one('hotel.reservation', string='Reservation')
    reservation_ids = fields.Many2many('hotel.reservation', 'hotel_reservation_transactions_rel','transaction_id','reservation_id',
                                    string='Reservation Orders', copy=False, readonly=True)
