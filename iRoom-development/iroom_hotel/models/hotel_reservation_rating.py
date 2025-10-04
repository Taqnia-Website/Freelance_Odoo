from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HotelReservationRating(models.Model):
    _name = 'hotel.reservation.rating'

    reservation_id = fields.Many2one('hotel.reservation', required=True)
    shop_id = fields.Many2one(related='reservation_id.shop_id')
    partner_id = fields.Many2one(related='reservation_id.partner_id')
    name = fields.Char()
    email = fields.Char()

    cleanliness = fields.Integer()
    comfort = fields.Integer()
    staff = fields.Integer()
    facilities_and_services = fields.Integer()
    total_rate = fields.Float('Total Rate', compute='_compute_total_rate', store=True)

    description = fields.Text()

    @api.depends('cleanliness', 'comfort', 'staff', 'facilities_and_services')
    def _compute_total_rate(self):
        for rating in self:
            rating.total_rate = (rating.cleanliness + rating.comfort + rating.staff + rating.facilities_and_services) / 4

    @api.onchange('cleanliness', 'comfort', 'staff', 'facilities_and_services')
    def _onchange_rates(self):
        for rating in self:
            error = 'rating must be from 1 to 5!'
            if rating.cleanliness > 5:
                raise ValidationError(_(f'Cleanliness {error}'))
            if rating.comfort > 5:
                raise ValidationError(_(f'Comfort {error}'))
            if rating.staff > 5:
                raise ValidationError(_(f'Staff {error}'))
            if rating.facilities_and_services > 5:
                raise ValidationError(_(f'Facilities and Services {error}'))
