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

class LeadTask(models.Model):
    _inherit = 'crm.lead'
    
    def view_task(self):
        return{
             'name': 'Task',
             'domain':[('lead_id', '=', self.id)],
             'view_type':'form',
             'res_model':'project.task',
             'view_id':	False,
             'view_mode':'tree,kanban,form',
             'type':'ir.actions.act_window',
             'target': 'current'
             }
   
    def action_task_count(self):
        task_count = self.env['project.task'].search_count([('lead_id','=',self.id)])
        self.task_count=task_count
            
    task_count = fields.Integer(compute="action_task_count")           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
