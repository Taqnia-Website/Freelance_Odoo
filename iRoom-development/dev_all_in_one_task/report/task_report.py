# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, models


class TaskReport(models.AbstractModel):
    _name = 'report.dev_all_in_one_task.template_task_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        records = self.env['project.task'].browse(docids)
        return {'doc_ids': records.ids,
                'doc_model': 'project.task',
                'docs': records,
                'data': data,
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
