from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    partner_id = fields.Many2one('res.partner', domain="[('agent', '=', False), ('is_supplier', '=', False)]")
    adults = fields.Integer('Adults', compute='compute_adults', store=True)
    childs = fields.Integer('Children', compute='compute_childs', store=True)

    @api.depends('reservation_line.adults')
    def compute_adults(self):
        for rec in self:
            rec.adults = sum([l.adults for l in rec.reservation_line])

    @api.depends('reservation_line.children')
    def compute_childs(self):
        for rec in self:
            rec.childs = sum([l.children for l in rec.reservation_line])

    def confirmed_reservation(self):
        res = super(HotelReservation, self).confirmed_reservation()
        for line in self.reservation_line:
            room_id = self.env['hotel.room'].search([('product_id', '=', line.room_number.id)])
            if room_id:
                room_id.room_state = 'confirmed'
        return res

    def done(self):
        res = super(HotelReservation, self).done()
        for line in self.reservation_line:
            room_id = self.env['hotel.room'].search([('product_id', '=', line.room_number.id)])
            if room_id:
                room_id.room_state = 'checked_in'
        return res
    
    # Start #
    def write(self, vals):
        """Update room_state when the reservation state changes."""
        res = super(HotelReservation, self).write(vals)
        if 'state' in vals:
            for reservation in self:
                for line in reservation.reservation_line:
                    room = self.env['hotel.room'].search([('product_id', '=', line.room_number.id)])
                    if room:
                        if vals['state'] == 'draft':
                            pass
                        elif vals['state'] == 'confirm':
                            pass
                        elif vals['state'] == 'cancel':
                            room.room_state = 'vacant'
                        elif vals['state'] == 'done':
                            pass
        return res
    # End #

class HotelReservationLine(models.Model):
    _inherit = 'hotel.reservation.line'

    adults = fields.Integer(default=1)
    children = fields.Integer(default=0)
    can_change_room_price = fields.Boolean()

    def compute_can_change_room_price(self):
        for rec in self:
            rec.can_change_room_price = False

    @api.model
    def default_get(self, default_fields):
        vals = super(HotelReservationLine, self).default_get(default_fields)
        if self.room_number:
            self.adults = self.room_number.max_adult
            self.children = self.room_number.max_child
        if self.env.user.has_group('iroom_custom.group_change_room_price'):
            self.can_change_room_price = True
        return vals

    @api.model
    def create(self, vals):
        if vals.get('room_number', False):
            room_id = self.env['hotel.room'].search([('product_id', '=', vals['room_number'])])
            if room_id and room_id.room_state == 'vacant':
                room_id.room_state = 'booking'
        res = super(HotelReservationLine, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('room_number', False):
            old_room_id = self.env['hotel.room'].search([('product_id', '=', self.room_number.id)])
            new_room_id = self.env['hotel.room'].search([('product_id', '=', vals['room_number'])])
            if old_room_id.id != new_room_id.id:
                old_room_id.room_state = 'vacant'
                new_room_id.room_state = 'booking'
        res = super(HotelReservationLine, self).write(vals)
        return res

    @api.onchange('room_number')
    def onchange_room_number(self):
        if self.room_number:
            room_id = self.env['hotel.room'].search([('product_id', '=', self.room_number.id)])
            self.adults = room_id.max_adult

    @api.constrains('adults')
    def validate_adults(self):
        for rec in self:
            if rec.adults > rec.room_number.max_adult:
                raise ValidationError(f"you can't exceed max adults for room {rec.room_number.name}")

    @api.constrains('children')
    def validate_children(self):
        for rec in self:
            if rec.children > rec.room_number.max_child:
                raise ValidationError(f"you can't exceed max children for room {rec.room_number.name}")
