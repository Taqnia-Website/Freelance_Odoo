from odoo import fields, models, api
import requests
import json
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    apply_channex = fields.Boolean(related='company_id.apply_channex', store=True)
    shop_id = fields.Many2one('sale.shop')
    room_type_id = fields.Many2one('hotel.room_type')
    children_fee = fields.Float()
    infant_fee = fields.Float()
    channex_id = fields.Char(string='Channex ID')
    meal_type = fields.Selection(selection=[
        ('all_inclusive', 'All Inclusive'), ('breakfast', 'Breakfast'), ('lunch', 'Lunch'),
        ('dinner', 'Dinner'), ('american', 'American'), ('bed_and_breakfast', 'Bed And Breakfast'),
        ('buffet_breakfast', 'Buffet Breakfast'), ('carribean_breakfast', 'Carribean Breakfast'), ('continental_breakfast', 'Continental Breakfast'),
        ('english_breakfast', 'English Breakfast'), ('european_plan', 'European Plan'), ('family_plan', 'Family Plan'),
        ('full_board', 'Full Board'), ('full_breakfast', 'FullBreakfast'), ('half_board', 'Half Board'),
        ('room_only', 'Room Only'), ('self_catering', 'Self Catering'), ('bermuda', 'Bermuda'),
        ('dinner_bed_and_breakfast_plan', 'Dinner Bed And Breakfast Plan'), ('family_american', 'Family American'), ('breakfast_and_lunch', 'Breakfast And Lunch'),
        ('lunch_and_dinner', 'Lunch And Dinner'),
    ])
    category_id = fields.Many2one('product.category')
    fixed_price = fields.Float()
    channex_notes = fields.Text()

    def button_create_channex_rate_plan(self):
        if self.apply_channex and self.shop_id.channex_id and self.room_type_id.channex_ids and self.category_id and self.fixed_price:
            # check room type is selected on the item
            room_type_line = self.room_type_id.channex_ids.filtered(lambda l: l.shop_id.id == self.shop_id.id)
            if not room_type_line:
                raise ValidationError("There is no Channex ID for this room type matching selected shop!")
            if self.category_id.id != self.room_type_id.cat_id.id:
                raise ValidationError("Room Type is not selected on items!")

            url = f"{self.company_id.channex_url}/rate_plans/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            payload = json.dumps({
                "rate_plan": {
                    "title": self.name,
                    "property_id": self.shop_id.channex_id,
                    "room_type_id": room_type_line.channex_id,
                    "options": [
                        {
                            "occupancy": self.room_type_id.normal_occupancy,
                            "is_primary": True,
                            "rate": str(self.fixed_price),
                            "children_fee": str(self.children_fee),
                            "infant_fee": str(self.infant_fee)
                        }
                    ],
                    "currency": self.currency_id.name,
                    "meal_type": self.meal_type,
                }
            })

            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)
            if data:
                self.channex_id = data.get('id', False)

    def update_channex_rate_plan(self, modified):
        url = f"{self.company_id.channex_url}/rate_plans/{self.channex_id}"
        vals = {}
        for f in modified:
            if f == "property_id":
                vals.update({
                    "property_id": self.shop_id.channex_id,
                })
            elif f == "room_type_id":
                room_type_line = self.room_type_id.channex_ids.filtered(lambda l: l.shop_id.id == self.shop_id.id)
                if not room_type_line:
                    raise ValidationError("There is no Channex ID for this room type matching selected shop!")
                vals.update({
                    "room_type_id": room_type_line.channex_id,
                })
            else:
                vals.update({
                    self.get_mapped_fields().get(f): getattr(self, f, None)
                })
        payload = json.dumps({
            "rate_plan": vals
        })
        headers = {
            "Content-Type": "application/json",
            "user-api-key": self.company_id.channex_key
        }
        response = requests.request("PUT", url, headers=headers, data=payload)

    def write(self, vals):
        res = super(Pricelist, self).write(vals)
        if self.apply_channex and self.channex_id:
            channex_fields = self.get_channex_fields()
            modified = [key for key in channex_fields if key in vals and vals.get(key, False)]
            if modified:
                self.update_channex_rate_plan(modified)
        return res

    def unlink(self):
        # todo implement remove endpoint
        return super(Pricelist, self).unlink()

    def get_channex_fields(self):
        return [
            "name", "property_id", "room_type_id", "meal_type",
            # "children_fee", "infant_fee", todo options
        ]

    def get_mapped_fields(self):
        return {
            "name": "title",
            "children_fee": "children_fee",
            "infant_fee": "infant_fee",
            "meal_type": "meal_type",
        }

class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    def write(self, vals):
        res = super(PricelistItem, self).write(vals)
        if vals.get('fixed_price', False):
            if self.pricelist_id.apply_channex and self.pricelist_id.channex_id:
                room_type_line = self.pricelist_id.room_type_id.channex_ids.filtered(lambda l: l.shop_id.id == self.pricelist_id.shop_id.id)
                if not room_type_line:
                    raise ValidationError("There is no Channex ID for this room type matching selected shop!")
                if self.categ_id.id != self.pricelist_id.room_type_id.cat_id.id:
                    raise ValidationError("Room Type is not selected on items!")

                self.update_channex_rate_plan(vals['fixed_price'])
        return res

    def update_channex_rate_plan(self, rate):
        url = f"{self.company_id.channex_url}/rate_plans/{self.pricelist_id.channex_id}"
        payload = json.dumps({
            "rate_plan": {
                "options": [
                    {
                        "occupancy": self.pricelist_id.room_type_id.normal_occupancy,
                        "is_primary": True,
                        "rate": str(rate),
                    }
                ]
            }
        })
        headers = {
            "Content-Type": "application/json",
            "user-api-key": self.company_id.channex_key
        }
        response = requests.request("PUT", url, headers=headers, data=payload)
    # todo add restrictions [availability - rate - min_stay_arrival - min_stay_through- min_stay- closed_to_arrival-closed_to_departure- stop_sell- max_stay]


    def button_update_restrictions(self):
        pricelist_id = self.pricelist_id
        if self.date_start and pricelist_id.shop_id.channex_id and pricelist_id.room_type_id.channex_ids and pricelist_id.category_id and self.fixed_price:
            # check room type is selected on the item
            room_type_line = pricelist_id.room_type_id.channex_ids.filtered(lambda l: l.shop_id.id == pricelist_id.shop_id.id)
            if not room_type_line:
                raise ValidationError("There is no Channex ID for this room type matching selected shop!")

            url = f"{self.company_id.channex_url}/restrictions/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            vals = {
                    "property_id": pricelist_id.shop_id.channex_id,
                    "rate_plan_id": pricelist_id.channex_id,
                    "rate": str(self.fixed_price),
                }
            if self.date_start and self.date_end:
                vals.update({
                    "date_from": self.date_start.strftime("%Y-%m-%d"),
                    "date_to": self.date_end.strftime("%Y-%m-%d"),
                })
            else:
                vals.update({
                    "date": self.date_start.strftime("%Y-%m-%d"),
                })
            payload = json.dumps({
                "values": [vals]
            })

            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)
            if data:
                if data[0].get('id', False):
                    if not pricelist_id.channex_notes:
                        pricelist_id.channex_notes = data[0]['id']
                    else:
                        pricelist_id.channex_notes += '\n'
                        pricelist_id.channex_notes += data[0]['id']
