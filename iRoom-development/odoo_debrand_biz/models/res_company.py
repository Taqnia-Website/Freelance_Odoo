# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

import base64
from odoo import api, http, fields, models, tools
from odoo.http import request
# from odoo.modules.module import get_resource_path

class Company(models.Model):
    _inherit = 'res.company'

    sys_tab_name = fields.Char(string="Tab Name", default="iRoom", readonly=False)
    odoo_replacement_text = fields.Char(string='Replace Text "Odoo" With?', default="iRoom")
