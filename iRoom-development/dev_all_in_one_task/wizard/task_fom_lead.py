# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models,api,_
from odoo.exceptions import ValidationError

class tomesheetaction(models.Model):
    _name = 'task.lead'
    
    project_id = fields.Many2one('project.project','Project', required='1')
    name = fields.Char('Task Name', required='1')
    dedline_date = fields.Date('Dedline Date')
    assigned_to = fields.Many2one('res.users','Assignees')
    lead_id = fields.Many2one('crm.lead')
 
    def update_values(self):
        active_id = self._context.get('active_id')
        project = self.env['project.task']
        values = {
         'project_id' : self.project_id.id,
         'name' : self.name,
         'date_deadline' : self.dedline_date,
         'user_ids' : self.assigned_to.ids,
         'lead_id' : active_id,
        }
        new_id = project.create(values)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
