# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo import models, tools
import base64
from odoo.http import request

class WebsiteInherit(models.Model):

    _inherit = "website"
    def _default_favicon(self):
        # img_path = get_resource_path('odoo_debrand_biz', 'static/img/icon.png')
        # with tools.file_open(img_path, 'rb') as f:
        #     return base64.b64encode(f.read())
        
        with tools.file_open('odoo_debrand_biz/static/img/iroom.png', 'rb') as f:
            return base64.b64encode(f.read())