# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import models, fields,api

class project(models.Model):
    _inherit = 'project.project'
    
    
    #@api.model
    #def create(self,vals):
    #    vals['project_seq'] = self.env['ir.sequence'].next_by_code('project.sequence.code') or 'New'
    #    return super(project,self).create(vals)	
    show_template_tasks = fields.Boolean(string="Default Tasks")
    @api.model
    def create(self, vals):
        # Set project sequence
        vals['project_seq'] = self.env['ir.sequence'].next_by_code('project.sequence.code') or 'New'
        
        # Create the project record
        res = super(project, self).create(vals)
        
        # Create template tasks if applicable
        if vals['show_template_tasks']:
            template_task_ids = self.env['task.template'].search([('is_template_task', '=', True)])
            for task in template_task_ids:
                self.env['project.task'].create({
                    'project_id': res.id,
                    'priority': task.priority or False,
                    'name': task.name,
                    'user_ids': [(4, user_id) for user_id in task.user_ids.ids],
                    'date_deadline': task.date_deadline or False,
                    'description': task.description or False,
                    'sequence': task.sequence or False,
                    'partner_id': task.partner_id.id if task.partner_id else False,
                    'email_cc': task.email_cc or False,
                    'displayed_image_id': task.displayed_image_id.id if task.displayed_image_id else False,
                    'tag_ids': [(6, 0, task.tag_ids.ids)] if task.tag_ids else False,
                    'date_assign': task.date_assign or False,
                    'date_last_stage_update': task.date_last_stage_update or False,
                    'company_id': task.company_id.id if task.company_id else False,
                })
        
        return res

        
        
    project_priority = fields.Selection(selection=[('0', 'Normal'),
                                                   ('1', 'Good'),
                                                   ('2', 'Very Good'),
                                                   ('3', 'Excellent')],
                                        string="Priority")
        
    project_seq = fields.Char(string="Number", readonly=True)
    task_user_assign_ids = fields.One2many('task.user.assignment', 'project_id', string='Task User Assignment')
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
