# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

class Company(models.Model):
    _inherit = 'res.company'

    task_closing_stage_id = fields.Many2one('project.task.type', string='Closing Stage')
    od_delay_reminder = fields.Boolean(string='Send Overdue Reminder',)
    od_first_reminder_days = fields.Integer(string='First Reminder(Days)')
    od_second_reminder_days = fields.Integer(string='Second Reminder(Days)')
    first_reminder = fields.Integer(string="First Reminder(Days)")
    second_reminder = fields.Integer(string="Second Reminder(Days)")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    task_closing_stage_id = fields.Many2one('project.task.type', domain=[('user_id', '=', False)],
                                            string='Closing Stage', related='company_id.task_closing_stage_id',
                                            readonly=False)
    od_delay_reminder = fields.Boolean(string='Send Overdue Reminder', related='company_id.od_delay_reminder', readonly=False)
    od_first_reminder_days = fields.Integer(string='First Reminder', related='company_id.od_first_reminder_days', readonly=False)
    od_second_reminder_days = fields.Integer(string='Second Reminder', related='company_id.od_second_reminder_days', readonly=False)
    first_reminder = fields.Integer(string="First Reminder(Days)", related='company_id.first_reminder', readonly=False)
    second_reminder = fields.Integer(string="Second Reminder(Days)", related='company_id.second_reminder', readonly=False)

    @api.onchange('first_reminder', 'second_reminder')
    def _check_days(self):
        if self.second_reminder > self.first_reminder:
            raise ValidationError("Second Reminder days must be less than First Reminder days")

    @api.onchange('od_first_reminder_days', 'od_second_reminder_days', 'od_delay_reminder')
    def _check_days(self):
        if self.od_delay_reminder:
            if self.od_first_reminder_days > 0 and self.od_second_reminder_days > 0:
                if self.od_first_reminder_days > self.od_second_reminder_days:
                    raise ValidationError(_('''Second Reminder must be greater than First Reminder'''))
                if self.od_first_reminder_days == self.od_second_reminder_days:
                    raise ValidationError(_('''Both reminder can to be same'''))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
