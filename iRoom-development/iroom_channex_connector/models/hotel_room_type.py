from odoo import fields, models, api, _
import requests
import json


class HotelRoomType(models.Model):
    _inherit = 'hotel.room_type'

    apply_channex = fields.Boolean(related='company_id.apply_channex', store=True)
    channex_ids = fields.One2many("hotel.room_type.channex", 'room_type_id')
    occ_adults = fields.Integer()
    normal_occupancy = fields.Integer()
    occ_children = fields.Integer()
    occ_infants = fields.Integer()
    channex_notes = fields.Text()

    def button_create_channex_room_type(self):
        if self.apply_channex:
            url = f"{self.company_id.channex_url}/room_types/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            channex_hotels = self.env['sale.shop'].search([('apply_channex', '=', True), ('channex_id', '!=', False)])
            vals = {
                "title": self.name,
                "occ_adults": self.occ_adults,
                "default_occupancy": self.normal_occupancy,
                "occ_children": self.occ_children,
                "occ_infants": self.occ_infants
            }
            for hotel in channex_hotels:
                count_of_rooms = self.env['hotel.room'].search_count([
                    ('categ_id', '=', self.cat_id.id), ('shop_id', '=', hotel.id)
                ])
                vals.update({
                    "property_id": hotel.channex_id,
                    "count_of_rooms": count_of_rooms,
                })
                payload = json.dumps({
                    "room_type": vals
                })

                response = requests.request("POST", url, headers=headers, data=payload)
                data = json.loads(response.text).get('data', False)
                if data:
                    self.write({
                        'channex_ids': [(0, 0, {
                            'shop_id': hotel.id,
                            'channex_id': data.get('id', False),
                        })],
                    })

    def update_channex_room_type(self, modified):
        for line in self.channex_ids:
            url = f"{self.company_id.channex_url}/room_types/{line.channex_id}"
            vals = {}
            for f in modified:
                vals.update({
                    self.get_mapped_fields().get(f): getattr(self, f, None)
                })
            payload = json.dumps({
                "room_type": vals
            })
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            response = requests.request("PUT", url, headers=headers, data=payload)

    def write(self, vals):
        res = super(HotelRoomType, self).write(vals)
        if self.apply_channex and self.channex_ids:
            channex_fields = self.get_channex_fields()
            modified = [key for key in channex_fields if key in vals and vals.get(key, False)]
            if modified:
                self.update_channex_room_type(modified)
        return res

    def unlink(self):
        # todo implement remove endpoint
        return super(HotelRoomType, self).unlink()

    def get_channex_fields(self):
        #     todo add count_of_rooms
        return [
            "name", "occ_adults", "normal_occupancy", "occ_children", "occ_infants",
        ]

    def get_mapped_fields(self):
        return {
            "name": "title",
            "occ_adults": "occ_adults",
            "occ_children": "occ_children",
            "occ_infants": "occ_infants",
            "normal_occupancy": "default_occupancy",
        }


class RoomTypeShopChannex(models.Model):
    _name = 'hotel.room_type.channex'
    _description = "Room Type Shop Channex"

    room_type_id = fields.Many2one('hotel.room_type')
    shop_id = fields.Many2one('sale.shop', string='Property/Hotel')
    channex_id = fields.Char(string='Channex ID')
