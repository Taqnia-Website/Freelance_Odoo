# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()
        config_parameter = request.env['ir.config_parameter'].sudo()
        res['odoo_replacement_text'] = config_parameter.get_param('odoo_replacement_text', 'iRoom')
        res['sys_tab_name'] = config_parameter.get_param('sys_tab_name', 'iRoom')
        
        return res