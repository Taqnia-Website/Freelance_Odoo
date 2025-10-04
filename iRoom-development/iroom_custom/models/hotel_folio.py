from odoo import fields, models, api
import pytz
from odoo.exceptions import ValidationError


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    def action_checkout(self):
        timezone = pytz.timezone(self.env.user.tz or 'UTC')
        for line in self.room_lines:
            checkout_date = pytz.utc.localize(line.checkout_date).astimezone(timezone).date()
            if checkout_date > fields.Date.today():
                raise ValidationError("you can't checkout early!")
        res = super(HotelFolio, self).action_checkout()
        for line in self.room_lines:
            room_id = self.env['hotel.room'].search([('product_id', '=', line.product_id.id)])
            if room_id:
                room_id.room_state = 'checked_out'
        return res


class HotelServiceLine(models.Model):
    _inherit = 'hotel_service.line'

    service_date = fields.Datetime(default=fields.Datetime.now)
    service_product_ids = fields.Many2many('product.product', compute='compute_service_product_ids', store=True)
    service_product_id = fields.Many2one('product.product', string='Room', domain="[('id', 'in', service_product_ids)]")

    @api.depends('folio_id.room_lines', 'folio_id.room_lines.product_id')
    def compute_service_product_ids(self):
        for rec in self:
            rec.service_product_ids = False
            if rec.folio_id and rec.folio_id.room_lines:
                products = rec.folio_id.room_lines.mapped('product_id').mapped('id')
                rec.service_product_ids = [(6, 0, products)]

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            pricelist = self.folio_id.pricelist_id.id
            price = self.env['product.pricelist']._price_get(self.product_id, self.product_uom_qty,uom=self.product_id.uom_id, date=self.service_date)[pricelist]
            self.price_unit = price
