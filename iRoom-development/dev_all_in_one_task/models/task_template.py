# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################
from odoo import models, fields, api, _

class task_template(models.Model):
    _inherit = 'project.task'
    _name = 'task.template'
    _description = 'Task Template'

    is_template_task = fields.Boolean(string="Template Task", default=True)

    parent_id = fields.Many2one(
        'task.template',  # This should point to the same model
        string='Parent Task',
        ondelete='cascade',  # Optional: define what happens when the parent is deleted
        index=True  # Optional: for performance
    )

    user_ids = fields.Many2many(
    'res.users',
    'task_template_user_rel',  # New relation table name
    'task_template_id',         # Column for task.template
    'user_id',                  # Corrected column for user
    string='Users'
)

    personal_stage_type_ids = fields.Many2many(
        'personal.stage.type',  # Assuming this is the model you want to relate to
        'task_template_personal_stage_rel',  # New relation table name
        'task_template_id',         # Column for task.template
        'stage_type_id',           # Column for personal stage type
        string='Personal Stages'
    )

    depend_on_ids = fields.Many2many(
    'project.task',  # Assuming this is the model you want to relate to
    'task_template_depend_on_rel',  # New relation table name
    'task_template_id',         # Column for task.template
    'depend_on_task_id',       # Column for depend_on task
    string='Depends On'
)

    dependent_ids = fields.Many2many(
    'project.task',  # Assuming this is the model you want to relate to
    'task_template_dependent_rel',  # New relation table name
    'task_template_id',         # Column for task.template
    'dependent_task_id',       # Column for dependent task
    string='Dependent Tasks'
)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
