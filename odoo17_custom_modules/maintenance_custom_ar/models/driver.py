# -*- coding: utf-8 -*-
from odoo import models, fields

class MaintenanceDriver(models.Model):
    _name = 'maintenance.driver'
    _description = 'سائق'
    _order = 'name'

    name = fields.Char(string='اسم السائق', required=True)
    phone = fields.Char(string='رقم الهاتف')
    license_number = fields.Char(string='رقم الرخصة')
    license_expiry = fields.Date(string='تاريخ انتهاء الرخصة')
    notes = fields.Text(string='ملاحظات')
    active = fields.Boolean(string='نشط', default=True)