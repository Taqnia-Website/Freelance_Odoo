from odoo import models, fields


class HotelRoomImage(models.Model):
    _name = 'hotel.room.image'

    image = fields.Image()

    room_id = fields.Many2one('hotel.room')
