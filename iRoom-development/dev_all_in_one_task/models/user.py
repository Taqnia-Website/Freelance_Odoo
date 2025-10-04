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
from datetime import timedelta, date, datetime


class Users(models.Model):
    _inherit = 'res.users'

    def deadline_date_list(self):
        deadline_date_list = []
        first_reminder_days = self.env.user.company_id.od_first_reminder_days
        second_reminder_days = self.env.user.company_id.od_second_reminder_days
        if first_reminder_days > 0:
            first_deadline_date = date.today() - timedelta(days=first_reminder_days)
            deadline_date_list.append(first_deadline_date)
        if second_reminder_days > 0:
            second_deadline_date = date.today() - timedelta(days=second_reminder_days)
            deadline_date_list.append(second_deadline_date)
        return deadline_date_list

    def get_overdue_task_details(self, user):
        task_details = []
        today = date.today()
        deadline_date_list = self.deadline_date_list()
        closing_stage_ids = self.env['project.task.type'].search([('fold', '=', True)])
        task_ids = self.env['project.task'].search([('date_deadline', 'in', deadline_date_list),
                                                    ('stage_id', 'not in', closing_stage_ids.ids),
                                                    ('user_ids', 'in', [user.id]),
                                                    ('project_id', '!=', False)])
        if task_ids:
            for task_id in task_ids:
                deadline = task_id.date_deadline.strftime('%d-%m-%Y')  # Format the date directly

                # Convert task_id.date_deadline to date before subtraction
                overdue_days = (today - task_id.date_deadline.date()).days  # Ensure both are date objects
                task_details.append({'name': task_id.name,
                                     'project': task_id.project_id.name,
                                     'deadline': deadline,
                                     'overdue_days': overdue_days})
        return task_details

    def task_overdue_reminder(self):
        if self.env.user.company_id.od_delay_reminder:
            deadline_date_list = self.deadline_date_list()
            if deadline_date_list:
                user_ids = self.env['res.users'].search([('share', '=', False)])
                closing_stage_ids = self.env['project.task.type'].search([('fold', '=', True)])
                for user_id in user_ids:
                    if closing_stage_ids:
                        task_ids = self.env['project.task'].search([('date_deadline', 'in', deadline_date_list),
                                                                    ('stage_id', 'not in', closing_stage_ids.ids),
                                                                    ('user_ids', 'in', [user_id.id]),
                                                                    ('project_id', '!=', False)])
                        if task_ids:
                            template_id = self.env.ref('dev_all_in_one_task.template_dev_task_overdue_reminder')
                            if template_id:
                                template_id.send_mail(user_id.id, force_send=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
