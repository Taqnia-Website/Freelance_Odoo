from odoo import fields, models, api


class HotelRoomType(models.Model):
    _inherit = "hotel.room_type"

    ntmp_room_type_id = fields.Many2one('ntmp.room.type', string='NTMP Type')
    apply_ntmp = fields.Boolean(related='company_id.apply_ntmp', store=True)
