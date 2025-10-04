# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = 'Checklist for Task'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    stage_id = fields.Many2one('project.task.type', string='Stage')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: