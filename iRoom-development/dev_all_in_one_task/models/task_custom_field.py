# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, fields, models, _

TYPE2FIELD = {
    'char': 'value_char',
    'float': 'value_float',
    'boolean': 'value_boolean',
    'integer': 'value_integer',
    'text': 'value_text',
    'binary': 'value_binary',
    'date': 'value_date',
    'datetime': 'value_datetime',
    'selection': 'attr_option',
}


# custom field main
class task_custom_fields(models.Model):
    _name = 'task.custom.fields'

    def get_task_model_id(self):
        task_m_id = self.env['ir.model'].search([('name', '=', 'Task')])
        return task_m_id

    name = fields.Char(string="Name", translate=True, required=True)
    task_model_id = fields.Many2one('ir.model', string="Model", required=True,
                                    ondelete="cascade",
                                    default=get_task_model_id, readonly=1)

    type = fields.Selection([('char', 'Char'),
                             ('float', 'Float'),
                             ('boolean', 'Boolean'),
                             ('integer', 'Integer'),
                             ('text', 'Text'),
                             ('binary', 'Binary'),
                             ('date', 'Date'),
                             ('datetime', 'DateTime'),
                             ('selection', 'Selection'),
                             ], required=True, default='char', index=True,
                            string='Date Type')

    task_custom_options = fields.One2many(
        'task.custom.field.option',
        'task_custom_id',
        string='Selection Custom Fields')

    task_custom_value_lines = fields.One2many('task.custom.field.values',
                                              'task_custom_id',
                                              string='Custom Field Values')


# custom field option
class task_custom_field_option(models.Model):
    _name = 'task.custom.field.option'

    name = fields.Char(string='Name')
    task_custom_id = fields.Many2one('task.custom.fields', string="Custom")


# custom field values
class task_custom_field_values(models.Model):
    _name = 'task.custom.field.values'

    # Default value for task_id
    @api.model
    def default_get(self, fields):
        defaults = super(task_custom_field_values, self).default_get(fields)
        active_id = self._context.get('t_id')
        if not active_id:
            return defaults
        defaults = {'t_id': active_id
                    }
        return defaults

    # to populate the value field in value ref
    @api.depends('value_float', 'value_integer', 'value_text', 'value_binary',
                 'value_datetime', 'value_date', 'value_char', 'value_boolean',
                 'task_custom_option')
    def task_compute_value_ref(self):
        for data in self:
            data_type = data.type
            field = TYPE2FIELD.get(data_type)
            if field:
                if data_type == 'selection':
                    data.value_ref = data.task_custom_option.name
                else:
                    data.value_ref = getattr(data, field)

    t_id = fields.Many2one('project.task', string="Task", readonly=1)
    task_custom_id = fields.Many2one('task.custom.fields', string="Custom")
    value_ref = fields.Char(string="Value", compute=task_compute_value_ref, store=True)
    type = fields.Selection(related='task_custom_id.type', store=True)
    task_custom_option = fields.Many2one('task.custom.field.option',
                                         string='Selection Options')
    value_float = fields.Float()
    value_integer = fields.Integer()
    value_boolean = fields.Boolean()
    value_char = fields.Char()
    value_text = fields.Text()
    value_binary = fields.Binary()
    value_date = fields.Date()
    value_datetime = fields.Datetime()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
