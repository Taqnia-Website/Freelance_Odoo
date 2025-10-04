from odoo import fields, models, api
import requests
import json
from datetime import date
from dateutil.relativedelta import relativedelta
import pytz


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    hotel_url_path = fields.Char(required=False)
    apply_channex = fields.Boolean(related='company_id.apply_channex', store=True)
    channex_id = fields.Char(string='Channex ID')
    channex_checkin_time = fields.Float(default=14.0)
    channex_checkin_from_time = fields.Float(default=14.0)
    channex_checkin_to_time = fields.Float(default=14.0)
    channex_checkout_time = fields.Float(default=13.0)
    channex_checkout_from_time = fields.Float(default=13.0)
    channex_checkout_to_time = fields.Float(default=13.0)
    channex_is_adults_only = fields.Boolean()
    channex_max_count_of_guests = fields.Integer(default=20)
    channex_pets_policy = fields.Selection(selection=[
        ('allowed', 'Allowed'), ('not_allowed', 'Not Allowed'),
        ('by_arrangements', 'By Arrangements'), ('assistive_only', 'Assistive Only'),
    ], default='not_allowed')
    channex_pets_non_refundable_fee = fields.Float()
    channex_pets_refundable_deposit = fields.Float()
    channex_smoking_policy = fields.Selection(selection=[
        ('no_smoking', 'No Smoking'), ('permitted_areas_only', 'Permitted Areas Only'), ('allowed', 'Allowed'),
    ], default='no_smoking')
    channex_internet_access_type = fields.Selection(selection=[
        ('none', 'None'), ('wifi', 'WiFi'), ('wired', 'Wired'),
    ], default='none')
    channex_internet_access_coverage = fields.Selection(selection=[
        ('entire_property', 'Entire Property'), ('public_areas', 'Public Areas'),
        ('all_rooms', 'All Rooms'), ('some_rooms', 'Some Rooms'),
        ('business_centre', 'Business Centre'),
    ])
    channex_internet_access_cost = fields.Float()
    channex_parking_type = fields.Selection(selection=[
        ('on_site', 'On Site'), ('nearby', 'Nearby'), ('none', 'None'),
    ], default='none')
    channex_parking_reservation = fields.Selection(selection=[
        ('not_available', 'Not Available'), ('not_needed', 'Not Needed'), ('needed', 'Needed'),
    ], default='not_needed')
    channex_parking_is_private = fields.Boolean()
    channex_policy_id = fields.Char()

    def button_create_channex_property(self):
        if self.apply_channex and not self.channex_id:
            url = f"{self.company_id.channex_url}/properties/"
            payload = json.dumps({
                "property": {
                    "title": self.name,
                    "currency": self.pricelist_id.currency_id.name,
                    "email": self.email,
                    "phone": self.mobile,
                    "website": self.website or '',
                    "logo_url": self.get_logo_url(),
                    "zip_code": self.company_id.zip,
                    "country": self.company_id.country_code,
                    "state": self.company_id.state_id.name,
                    "city": self.company_id.city,
                    "address": self.address,
                    "latitude": self.x_coordinate,
                    "longitude": self.y_coordinate,
                    "group_id": self.company_id.channex_id
                }
            })
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)
            if data:
                self.channex_id = data.get('id', False)

    def update_channex_property(self, modified):
        url = f"{self.company_id.channex_url}/properties/{self.channex_id}"
        vals = {}
        for f in modified:
            if f == "pricelist_id":
                vals.update({
                    "currency": self.pricelist_id.currency_id.name,
                })
            elif f == "shop_img":
                vals.update({
                    "logo_url": self.get_logo_url(),
                })
            else:
                vals.update({
                    self.get_mapped_fields().get(f): getattr(self, f, None)
                })
        payload = json.dumps({
            "property": vals
        })
        headers = {
            "Content-Type": "application/json",
            "user-api-key": self.company_id.channex_key
        }
        response = requests.request("PUT", url, headers=headers, data=payload)

    def write(self, vals):
        res = super(SaleShop, self).write(vals)
        if self.apply_channex and self.channex_id:
            channex_fields = self.get_channex_fields()
            modified = [key for key in channex_fields if key in vals and vals.get(key, False)]
            if modified:
                self.update_channex_property(modified)
        return res

    def get_channex_fields(self):
        return [
            "name", "pricelist_id", "email", "mobile", "website", "shop_img", "address", "x_coordinate", "y_coordinate"
        ]

    def get_mapped_fields(self):
        return {
            "name": "title",
            "email": "email",
            "mobile": "phone",
            "website": "website",
            "address": "address",
            "x_coordinate": "latitude",
            "y_coordinate": "longitude",
        }

    def get_logo_url(self):
        return f"{self.company_id.get_base_url()}/web/image?model=sale.shop&id={self.id}&field=shop_img"

    def prepare_channex_policy_vals(self):
        vals = {
            "title": f"{self.name} Policy",
            "currency": self.company_id.currency_id.name,
            "is_adults_only": self.channex_is_adults_only,
            "max_count_of_guests": self.channex_max_count_of_guests,
            "checkin_time": self.format_channex_time(self.channex_checkin_time),
            "checkin_from_time": self.format_channex_time(self.channex_checkin_from_time),
            "checkin_to_time": self.format_channex_time(self.channex_checkin_to_time),
            "checkout_time": self.format_channex_time(self.channex_checkout_time),
            "checkout_from_time": self.format_channex_time(self.channex_checkout_from_time),
            "checkout_to_time": self.format_channex_time(self.channex_checkout_to_time),
            "internet_access_type": self.channex_internet_access_type,
            "parking_type": self.channex_parking_type,
            "parking_reservation": self.channex_parking_reservation,
            "pets_policy": self.channex_pets_policy,
            "smoking_policy": "no_smoking"
        }
        if self.channex_internet_access_type in ['wifi', 'wired']:
            vals.update({
                "internet_access_cost": str(self.channex_internet_access_cost),
                "internet_access_coverage": self.channex_internet_access_coverage,
            })
        if self.channex_parking_type in ['nearby', 'on_site']:
            vals.update({
                "parking_is_private": self.channex_parking_is_private,
            })
        if self.channex_pets_policy in ['allowed', 'assistive_only', 'by_arrangements']:
            vals.update({
                "pets_non_refundable_fee": str(self.channex_pets_non_refundable_fee),
                "pets_refundable_deposit": str(self.channex_pets_refundable_deposit),
            })
        return vals

    def button_sync_channex_policy(self):
        vals = self.prepare_channex_policy_vals()
        if self.apply_channex and self.channex_id and not self.channex_policy_id:
            url = f"{self.company_id.channex_url}/hotel_policies/"
            payload = json.dumps({
                "hotel_policy": vals
            })
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            data = json.loads(response.text).get('data', False)
            if data:
                self.channex_policy_id = data.get('id', False)
        elif self.channex_policy_id:
            url = f"{self.company_id.channex_url}/hotel_policies/{self.channex_policy_id}"
            payload = json.dumps({
                "hotel_policy": vals
            })
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            response = requests.request("PUT", url, headers=headers, data=payload)
            # x = 1

    def button_create_channex_images(self):
        if self.channex_id:
            url = f"{self.company_id.channex_url}/photos/"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": self.company_id.channex_key
            }
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for image in self.image_ids:
                payload = json.dumps({
                    "photo": {
                        "author": self.name,
                        "description": "Room View",
                        "kind": "photo",
                        "position": 0,
                        "url": f"{base_url}/web/image?model=sale.shop.image&id={image.id}&field=image",
                        "property_id": "52397a6e-c330-44f4-a293-47042d3a3607",
                    }
                })

                response = requests.request("POST", url, headers=headers, data=payload)
                data = json.loads(response.text).get('data', False)
                x  = 1

    def format_channex_time(self, time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(time * 60, 60))

    # full sync
    def action_channex_full_sync_availability(self):
        room_types = self.env['hotel.room_type'].search([('company_id', '=', self.company_id.id)])
        timezone = pytz.timezone(self.env.user.tz or 'UTC')
        vals = []
        for room_type in room_types:
            start_date = date.today()
            end_date = start_date + relativedelta(days=500)
            room_category = room_type.cat_id
            total_rooms = self.env['hotel.room'].search_count([('categ_id', '=', room_category.id)])
            all_booked = self.env['hotel.reservation.line'].search([
                ('line_id.state', '=', 'confirm'), ('categ_id', '=', room_category.id)
            ])
            all_occupied = self.env['hotel_folio.line'].search([
                ('folio_id.state', 'in', ['draft', 'sent', 'sale', 'progress']), ('categ_id', '=', room_category.id)
            ])
            all_on_maintenance = self.env['rr.housekeeping'].search([
                ('state', '!=', 'draft'), ('room_no.categ_id', '=', room_category.id)
            ])
            while start_date <= end_date:
                booked = len([l for l in all_booked if pytz.utc.localize(l.checkin).astimezone(timezone).date() <= start_date < pytz.utc.localize(l.checkout).astimezone(timezone).date()])
                occupied = len([l for l in all_occupied if pytz.utc.localize(l.checkin_date).astimezone(timezone).date() <= start_date < pytz.utc.localize(l.checkout_date).astimezone(timezone).date()])
                on_maintenance = len([l for l in all_on_maintenance if pytz.utc.localize(l.date).astimezone(timezone).date() == start_date])
                vals.append((0, 0, {
                    'room_type_id': room_type.id,
                    'date_from': start_date,
                    'availability': total_rooms - booked - occupied - on_maintenance
                }))
                start_date += relativedelta(days=1)

        wizard = self.env['channex.update.availability'].create({
            'property_id': self.id,
            'line_ids': vals
        })
        wizard.action_update_availability()

    def action_channex_full_sync_rate(self):
        room_types = self.env['hotel.room_type'].search([('company_id', '=', self.company_id.id)])
        timezone = pytz.timezone(self.env.user.tz or 'UTC')
        vals = []
        for room_type in room_types:
            pricelists = self.env['product.pricelist'].search([('room_type_id', '=', room_type.id)])
            for pricelist in pricelists:
                pricelist_items = pricelist.item_ids
                for item in pricelist_items:
                    date_from = pytz.utc.localize(item.date_start).astimezone(timezone).date()
                    date_to = False
                    if item.date_end:
                        date_to = pytz.utc.localize(item.date_end).astimezone(timezone).date()
                    vals.append((0, 0, {
                        'room_type_id': room_type.id,
                        'pricelist_id': pricelist.id,
                        'rate': item.fixed_price,
                        'date_from': date_from,
                        'date_to': date_to,
                    }))

        wizard = self.env['channex.update.rate'].create({
            'company_id': self.company_id.id,
            'restrict_rate': True,
            'line_ids': vals
        })
        wizard.action_update_rate()

    def cron_channex_full_sync(self):
        companies = self.env['res.company'].sudo().search([('apply_channex', '=', True), ('channex_id', '!=', False)])
        for company in companies:
            shops = self.env['sale.shop'].sudo().search([('channex_id', '!=', False), ('company_id', '=', company.id)])
            for shop in shops:
                shop.action_channex_full_sync_availability()
                shop.action_channex_full_sync_rate()
