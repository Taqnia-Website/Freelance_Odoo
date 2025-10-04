from odoo import fields, models, api


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    def _default_category_id(self):
        return [(6,
                 0,
                 [self.env.ref('iroom_hotel_agent_fix_bugs.res_partner_category_guest').id]
                )]
    def _compute_category_id(self):
        for category in self:
            category.category_id =  [(6,
                 0,
                 [self.env.ref('iroom_hotel_agent_fix_bugs.res_partner_category_guest').id]
                )]

    category_id = fields.Many2many('res.partner.category',
                                   compute=_compute_category_id,
                                   default=_default_category_id)