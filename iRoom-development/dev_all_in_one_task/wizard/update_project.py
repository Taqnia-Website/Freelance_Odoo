# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class UpdateTask(models.TransientModel):
    _name = 'update.project'

    select_id = fields.Selection([('users_id', 'Users'),
                                  ('date', 'Date'),
                                  ('tags_ids', 'Tags'),
                                  ('stage_id', 'Stage')], string='Update')

    user_ids = fields.Many2many('res.users', string='Users')
    date_deadline = fields.Date(string='Date')
    tag_ids = fields.Many2many('project.tags', string='Tag')
    stage_id = fields.Many2one('project.task.type', string='Stage')

    def update_values(self):
        active_id = self._context.get('active_ids')
        update_ids = self.env['project.task'].browse(active_id)
        for line in update_ids:
            if self.user_ids:
                line.user_ids = [(6, 0, self.user_ids.ids)]
            if self.date_deadline:
                line.date_deadline = self.date_deadline
            if self.tag_ids:
                line.tag_ids = self.tag_ids
            if self.stage_id:
                line.stage_id = self.stage_id
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
