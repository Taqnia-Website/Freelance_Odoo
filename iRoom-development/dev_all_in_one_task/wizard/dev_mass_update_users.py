# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

import time
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class dev_mass_update_users(models.TransientModel):
    _name = "dev.mass.update.users"
    _description = "Mass Update Users"
    
   
    user_ids = fields.Many2many('res.users',string="Users", required=True)
    
    def update_user(self):
        active_ids = self._context.get('active_ids') 
        task_ids = self.env['project.task'].browse(active_ids)
        task_ids.write({'user_ids':self.user_ids.ids})
        return True 
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
