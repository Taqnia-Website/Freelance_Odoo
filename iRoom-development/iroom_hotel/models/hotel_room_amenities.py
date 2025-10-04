from odoo import models, fields


class HotelRoomAmenities(models.Model):
    _inherit = 'hotel.room_amenities'

    icon_code = fields.Char()
