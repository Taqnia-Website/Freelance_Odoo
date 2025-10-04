
from odoo import api, exceptions, fields, models, _



class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

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

    def search_folio(self, shop_id):
        if self.env.user.partner_id.agent:
            shop_id = int(shop_id)
            lines = self.env['hotel_folio.line'].search([
                ('folio_id.shop_id', '=', shop_id),
                ('folio_id.reservation_id', '!=', False)
            ])
            folios = [
                {
                    'checkin': fo_ln.checkin_date,
                    'checkout': fo_ln.checkout_date,
                    'status': fo_ln.folio_id.state,
                    'id': fo_ln.folio_id.id,
                    'room_name': fo_ln.product_id.name,
                    'fol_no': fo_ln.folio_id.reservation_id.reservation_no,
                } for fo_ln in lines
            ]
            return folios
        return super().search_folio(shop_id)

    def create_detail(self,room_type,room,checkin,checkout):

        # Inherit this function to prevent to create a reservation via Dashboard once selected the zone.
        if not self.env.user.has_group('hotel_management.group_hotel_reservation_manager') or not self.env.user.has_group('hotel_management.group_hotel_reservation_user'):
            raise exceptions.AccessError(_('You do not have permission to make reservations. Please contact your system administrator for assistance'))

        return super().create_detail(room_type,room,checkin,checkout)

