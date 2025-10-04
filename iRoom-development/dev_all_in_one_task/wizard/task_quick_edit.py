# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import models, api,fields

class task_quick_edit(models.TransientModel):
    _name = "task.quick.edit"
    _description = "Task Quick Edit"
    


    @api.model
    def default_get(self, fields):
        vals = super(task_quick_edit, self).default_get(fields)
        active_id = self._context.get('active_id')
        print('=============active_id=============',active_id)
        task_id = self.env['project.task'].browse(active_id)
        vals.update({'name':task_id.name or '',
                     'user_ids':[(6, 0, task_id.user_ids.ids)],
                     'tag_ids':[(6, 0, task_id.tag_ids.ids)],
                     'date_deadline':task_id.date_deadline or ''
                   })
        print('vals=========================',vals)
        return vals


  
    name = fields.Char('Task',required="1")
    user_ids = fields.Many2many('res.users',string="Assignees")
    tag_ids = fields.Many2many('project.tags',string="Tags")
    date_deadline = fields.Date(string="Deadline")


    def confirm_task(self):
        active_id = self._context.get('active_id') 
        task_id = self.env['project.task'].browse(active_id)
        task_id.write({'name':self.name,
                       'user_ids':self.user_ids.ids or False,
                       'tag_ids': [(6, 0, self.tag_ids.ids)],
                       'date_deadline':self.date_deadline or '',
                      })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
