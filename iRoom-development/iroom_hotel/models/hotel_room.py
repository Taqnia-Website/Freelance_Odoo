from odoo import models, fields


class HotelRoom(models.Model):
    _inherit = 'hotel.room'

    brief = fields.Char(translate=True)
    image_ids = fields.One2many('hotel.room.image', 'room_id')
    number_of_bathrooms = fields.Integer()
    area = fields.Integer()
