from odoo import fields, models, api
import requests
import json


class Company(models.Model):
    _inherit = 'res.company'

    apply_channex = fields.Boolean()
    channex_key = fields.Char()
    channex_url = fields.Char(string='Channex URL')
    channex_id = fields.Char(string='Channex ID')

    def write(self, vals):
        res = super(Company, self).write(vals)
        if self.apply_channex and self.channex_key and self.channex_url and not self.channex_id:
            url = f"{self.channex_url}/groups/"
            payload = json.dumps({
                "group": {
                    "title": self.name
                }
            })
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.channex_key
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)
            if data:
                self.channex_id = data.get('id', False)
        return res

    def action_get_channex_property(self):
        if self.apply_channex:
            url = f"{self.channex_url}/properties/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.channex_key
            }
            response = requests.request("GET", url, headers=headers)
            data_list = json.loads(response.text).get('data', False)
            if data_list:
                payment_term_id = self.env['account.payment.term'].search([], limit=1)
                for data in data_list:
                    if data.get('id', False):
                        attributes = data['attributes']
                        self.env['sale.shop'].create({
                            'channex_id': data['id'],
                            'name': attributes.get('title', ''),
                            'payment_default_id': payment_term_id.id,
                            'email': attributes.get('email', ''),
                            'mobile': attributes.get('phone', ''),
                            'address': attributes.get('address', ''),
                            'company_id': self.id,
                        })

    def action_get_channex_room_types(self):
        if self.apply_channex:
            url = f"{self.channex_url}/room_types/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.channex_key
            }
            response = requests.request("GET", url, headers=headers)
            data_list = json.loads(response.text).get('data', False)
            if data_list:
                for data in data_list:
                    if data.get('id', False):
                        lines = []
                        property_id = data["relationships"]["property"]["data"]["id"]
                        shop_id = self.env['sale.shop'].search([('channex_id', '=', property_id)])
                        if shop_id:
                            lines.append((0, 0, {
                                'shop_id': shop_id.id,
                                'channex_id': data['id']
                            }))
                        attributes = data['attributes']
                        self.env['hotel.room_type'].create({
                            'name': attributes.get('title', ''),
                            'occ_infants': attributes.get('occ_infants', ''),
                            'occ_children': attributes.get('occ_children', ''),
                            'occ_adults': attributes.get('occ_adults', ''),
                            'normal_occupancy': attributes.get('default_occupancy', ''),
                            'company_id': self.id,
                            'channex_ids': lines
                        })

    def action_get_channex_rate_plans(self):
        if self.apply_channex:
            url = f"{self.channex_url}/rate_plans/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.channex_key
            }
            response = requests.request("GET", url, headers=headers)
            data_list = json.loads(response.text).get('data', False)
            if data_list:
                for data in data_list:
                    if data.get('id', False):
                        property_id = data["relationships"]["property"]["data"]["id"]
                        shop_id = self.env['sale.shop'].search([('channex_id', '=', property_id)])
                        room_type_id = data["relationships"]["room_type"]["data"]["id"]
                        room_type = self.env['hotel.room_type.channex'].search([('channex_id', '=', room_type_id), ('room_type_id', '!=', False)], limit=1)
                        if shop_id and room_type:
                            rate = 0
                            attributes = data['attributes']
                            options = attributes['options']
                            if options:
                                rate = options[0]['rate']
                            self.env['product.pricelist'].create({
                                'name': attributes.get('title', ''),
                                'company_id': self.id,
                                'shop_id': shop_id.id,
                                'room_type_id': room_type.room_type_id.id,
                                'channex_id': data['id'],
                                'infant_fee': attributes.get('infant_fee', 0),
                                'children_fee': attributes.get('children_fee', 0),
                                'fixed_price': rate,
                            })
