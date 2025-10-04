from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import requests
import json


class ChannexUpdateRate(models.TransientModel):
    _name = 'channex.update.rate'
    _description = 'Channex Update Rate'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    channex_notes = fields.Text()
    line_ids = fields.One2many('channex.update.rate.line', 'wizard_id')
    restrict_rate = fields.Boolean(string='Rate')
    restrict_min_stay = fields.Boolean(string='Min Stay')
    restrict_max_stay = fields.Boolean(string='Max Stay')
    restrict_stop_sell = fields.Boolean(string='Stop Sell')
    restrict_closed_to_arrival = fields.Boolean(string='Closed to Arrival')
    restrict_closed_to_departure = fields.Boolean(string='Closed to Departure')

    def action_update_rate(self):
        url = f"{self.company_id.channex_url}/restrictions/"
        headers = {
            "Content-Type": "application/json",
            "user-api-key": self.company_id.channex_key
        }
        val_list = []
        for line in self.line_ids:
            room_type_line = line.room_type_id.channex_ids.filtered(lambda l: l.shop_id.id == line.pricelist_id.shop_id.id)
            if not room_type_line:
                raise ValidationError("There is no Channex ID for this room type matching selected shop!")

            vals = {
                "property_id": line.pricelist_id.shop_id.channex_id,
                "rate_plan_id": line.pricelist_id.channex_id,
            }
            if self.restrict_rate:
                vals.update({"rate": str(line.rate)})
            if self.restrict_min_stay:
                vals.update({"min_stay": line.min_stay})
            if self.restrict_max_stay:
                vals.update({"max_stay": line.max_stay})
            if self.restrict_stop_sell:
                vals.update({"stop_sell": int(line.stop_sell)})
            if self.restrict_closed_to_arrival:
                vals.update({"stop_sell": int(line.closed_to_arrival)})
            if self.restrict_closed_to_departure:
                vals.update({"stop_sell": int(line.closed_to_departure)})
            if line.date_from and line.date_to:
                vals.update({
                    "date_from": line.date_from.strftime("%Y-%m-%d"),
                    "date_to": line.date_to.strftime("%Y-%m-%d"),
                })
            else:
                vals.update({
                    "date": line.date_from.strftime("%Y-%m-%d"),
                })
            val_list.append(vals)
        payload = json.dumps({
            "values": val_list
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
            'name': _('Update Rate'),
            'res_model': 'channex.update.rate',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
        }


class ChannexUpdateRateLine(models.TransientModel):
    _name = 'channex.update.rate.line'
    _description = 'Channex Update Rate Line'

    wizard_id = fields.Many2one('channex.update.rate')
    room_type_id = fields.Many2one('hotel.room_type', required=True)
    pricelist_id = fields.Many2one('product.pricelist', domain="[('room_type_id', '=', room_type_id)]", required=True)
    date_from = fields.Date(required=True, string='From')
    date_to = fields.Date(string='To')
    rate = fields.Float()
    min_stay = fields.Integer()
    max_stay = fields.Integer()
    stop_sell = fields.Boolean()
    closed_to_arrival = fields.Boolean()
    closed_to_departure = fields.Boolean()

    @api.constrains('date_from', 'date_to')
    def validate_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError("From date can't be after To date")

    @api.constrains('min_stay')
    def validate_min_stay(self):
        for rec in self:
            if rec.min_stay < 0:
                raise ValidationError("Min Stay accept positive values only")

    @api.constrains('max_stay')
    def validate_max_stay(self):
        for rec in self:
            if rec.max_stay < 0:
                raise ValidationError("Max Stay accept positive values only")
