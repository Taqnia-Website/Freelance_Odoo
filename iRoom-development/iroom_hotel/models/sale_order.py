from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_room_id = fields.Many2one('product.product')
    reservation_from = fields.Datetime()
    reservation_to = fields.Datetime()
    number_of_adults = fields.Integer()
    number_of_children = fields.Integer()
    reservation_id = fields.Many2one('hotel.reservation')

    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            reservation = self.env['hotel.reservation'].sudo().create({
                'partner_id': order.partner_id.id,
                'pricelist_id': order.partner_id.property_product_pricelist.id or 1,
                'shop_id': order.product_room_id.shop_id.id,
                'adults': order.number_of_adults,
                'childs': order.number_of_children,
                'source': 'through_web',
                'reservation_line': [(0, 0, {
                    'checkin': order.reservation_from,
                    'checkout': order.reservation_to,
                    'categ_id': order.product_room_id.categ_id.id,
                    'room_number': order.product_room_id.id,
                    'price': order.product_room_id.lst_price
                })]
            })
            reservation.confirmed_reservation()
            order.reservation_id = reservation.id
