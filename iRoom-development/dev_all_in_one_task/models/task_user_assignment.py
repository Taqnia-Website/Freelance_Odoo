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


class TaskUserAssignment(models.Model):
    _name = 'task.user.assignment'
    _description = 'Task User Assignment'

    _sql_constraints = [('stage_user_unique', 'unique (stage_id, user_id, project_id)', 'Stage and Assign To combination must be unique'),
                        ('stage_unique', 'unique (stage_id, project_id)', 'Stage is already configured')]

    project_id = fields.Many2one('project.project', string='Project', copy=False, ondelete='cascade') # link
    stage_id = fields.Many2one('project.task.type', string='Stage', required=True)
    user_id = fields.Many2one('res.users', string='Assign To',  required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: