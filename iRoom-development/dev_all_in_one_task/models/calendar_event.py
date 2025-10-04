# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError

class calendar_event(models.Model):
    _inherit = 'calendar.event'

    def copy(self, default=None):
        if default is None:
            default = {}
        default['project_id'] = False
        default['task_id'] = False
        return super(calendar_event, self).copy(default)

    def action_create_task(self):
        if not self.task_id:
            name = 'Task from : ' + self.name
            task_id = self.env['project.task'].create({'name': name,})
            task_id.meeting_id = self.id
            self.task_id = task_id.id
            if task_id.project_id:
                self.project_id = self.task_id.project_id.id
        else:
            raise ValidationError(_("This Meeting has already Task Assigned"))

    def action_view_task(self):
        if not self.task_id:
            raise ValidationError(_("There is no Task from this Meeting."))
        form_view = self.env.ref('project.view_task_form2')
        return {
            'name': 'Task',
            'res_model': 'project.task',
            'res_id': self.task_id.id,
            'views': [(form_view.id, 'form')],
            'type': 'ir.actions.act_window',
        }

    project_id = fields.Many2one("project.project", string="Project")
    task_id = fields.Many2one("project.task", string="Task")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
