from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HotelRoomAmenities(models.Model):
    _inherit = 'hotel.room_amenities'

    @api.model
    def create(self, vals):
        if vals.get('categ_id', False):
            category = self.env['product.category'].browse(vals['categ_id'])
            if not category.isamenitype:
                raise ValidationError("please select amenity category!")
        res = super(HotelRoomAmenities, self).create(vals)
        return res
