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


class end_task(models.TransientModel):
    _name = "end.task.wizard"

    task_start_date = fields.Datetime("Start Date")
    description = fields.Char("Description", required="1")
    end_date = fields.Datetime("End Date", default=fields.Datetime.now)
    duration = fields.Char("Duration")

    def generate_timesheet(self):
        active_id = self._context.get('active_ids')[0]
        task_id = self.env['project.task'].browse(active_id)
        duration = self.duration.replace(':', '.')

        data = {'date': fields.Date.today(),
                'name': self.description,
                'project_id': task_id.project_id and task_id.project_id.id or False,
                'task_id': active_id or False,
                'unit_amount': float(duration),

                }
        self.env['account.analytic.line'].create(data)
        task_id.task_start_date = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
