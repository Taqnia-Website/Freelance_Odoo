from odoo import api, exceptions, fields, models, _, exceptions

class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'


    def unlink(self):
        for category in self:
            if category.id == self.env.ref('hotel_management.res_partner_category_guest').id:
                raise exceptions.UserError(_(f"The partner tag {self.env.ref('iroom_hotel_agent_fix_bugs.res_partner_category_guest').name} cannot be deleted as it is a required system tag used for filtering guest name fields in Reservation and Folio documents."))

        return super().unlink()