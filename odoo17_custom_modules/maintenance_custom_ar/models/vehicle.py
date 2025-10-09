# -*- coding: utf-8 -*-
from odoo import models, fields

class MaintenanceVehicle(models.Model):
    _name = 'maintenance.vehicle'
    _description = 'مركبة'
    _order = 'name'

    name = fields.Char(string='اسم المركبة', required=True)
    vehicle_type = fields.Char(string='نوع السيارة', required=True)
    plate_number = fields.Char(string='رقم اللوحة')
    model = fields.Char(string='الموديل')
    year = fields.Integer(string='سنة الصنع')
    color = fields.Char(string='اللون')
    notes = fields.Text(string='ملاحظات')
    active = fields.Boolean(string='نشط', default=True)