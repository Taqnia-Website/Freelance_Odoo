# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    # فيلد وهمي لتجنّب كراش الواجهة
    dr_has_custom_module = fields.Boolean(
        string='Has Custom Module',
        default=False,
        # نخزّنه في ir.config_parameter عشان ما يعملش مشاكل
        config_parameter='hr_custom_ar.dr_has_custom_module'
    )
