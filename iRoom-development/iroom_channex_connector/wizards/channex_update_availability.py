from odoo import fields, models, api, _
import requests
import json
from odoo.exceptions import ValidationError


class ChannexUpdateAvailability(models.TransientModel):
    _name = 'channex.update.availability'
    _description = 'Channex Update Availability'

    property_id = fields.Many2one('sale.shop', required=True)
    line_ids = fields.One2many('channex.update.availability.line', 'wizard_id')
    channex_notes = fields.Text()

    def action_update_availability(self):
        if self.property_id.channex_id:
            company = self.property_id.company_id
            url = f"{company.channex_url}/availability/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": company.channex_key
            }
            vals_lst = []
            for line in self.line_ids:
                room_type_line = line.room_type_id.channex_ids.filtered(lambda l: l.shop_id.id == self.property_id.id)
                total_rooms = self.env['hotel.room'].search_count([('categ_id', '=', line.room_type_id.cat_id.id)])
                # if  line.availability > total_rooms:
                #     raise ValidationError(f"availability is more than total rooms of type {self.room_type_id.name}")
                vals = {
                    "property_id": self.property_id.channex_id,
                    "room_type_id": room_type_line.channex_id,
                    "availability": line.availability
                }
                if line.date_from and line.date_to:
                    vals.update({
                        "date_from": line.date_from.strftime("%Y-%m-%d"),
                        "date_to": line.date_to.strftime("%Y-%m-%d"),
                    })
                else:
                    vals.update({
                        "date": line.date_from.strftime("%Y-%m-%d"),
                    })
                vals_lst.append(vals)
            payload = json.dumps({
                "values": vals_lst
            })
            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)
            if data:
                if data[0].get('id', False):
                    if not self.channex_notes:
                        self.channex_notes = data[0]['id']
                    else:
                        self.channex_notes += '\n'
                        self.channex_notes += data[0]['id']
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update Availability'),
            'res_model': 'channex.update.availability',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
        }


class ChannexUpdateAvailabilityLine(models.TransientModel):
    _name = 'channex.update.availability.line'
    _description = 'Channex Update Availability Line'


    wizard_id = fields.Many2one('channex.update.availability')
    room_type_id = fields.Many2one('hotel.room_type')
    date_from = fields.Date(required=True)
    date_to = fields.Date()
    availability = fields.Integer()

    @api.constrains('date_from', 'date_to')
    def validate_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError("From date can't be after To date")
