# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

import base64, os
from odoo import api, http, fields, models, tools, _
from odoo.http import request

class IrDefault(models.Model):
    _inherit = 'ir.default'
    
    @api.model
    def set_system_favicon(self, model, field):
        script_dir = os.path.dirname(__file__)
        rel_path = "../static/src/img/iroom.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            self.set('res.config.settings', 'system_favicon', encoded_string.decode("utf-8"))


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    system_favicon = fields.Binary(related='website_id.favicon',
                            string="Tab Favicon", readonly=False)
    sys_tab_name = fields.Char(related='company_id.sys_tab_name',
                           string="Tab Name", readonly=False)
    odoo_replacement_text = fields.Char(string='Replace Text "Odoo" With?', related='company_id.odoo_replacement_text',readonly=False)

    @api.model
    def get_debrand_settings(self):
        IrDefault = self.env['ir.default'].sudo()
        system_favicon = IrDefault._get('res.config.settings', "system_favicon")
        sys_tab_name = IrDefault._get('res.config.settings', "sys_tab_name")
        odoo_replacement_text = IrDefault._get('res.company', "odoo_replacement_text")
        return {
            'system_favicon': system_favicon,
            'sys_tab_name': sys_tab_name,
            'odoo_replacement_text': odoo_replacement_text,
        }

    @api.model
    def get_values(self):
        res = super(ResConfig, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        odoo_replacement_text = ir_config.get_param('odoo_replacement_text', default='Synozon Technology')
        system_favicon = ir_config.get_param('system_favicon')
        sys_tab_name = ir_config.get_param('sys_tab_name', default="Synozon Technology")
        res.update(
            odoo_replacement_text=odoo_replacement_text,
            system_favicon=system_favicon,
            sys_tab_name=sys_tab_name,
        )
        return res

    def set_values(self):
        super(ResConfig, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("odoo_replacement_text", self.odoo_replacement_text or "")
        ir_config.set_param("system_favicon", self.system_favicon or "")
        ir_config.set_param("sys_tab_name", self.sys_tab_name or "")
