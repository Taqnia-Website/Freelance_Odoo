# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class meeting_from_task(models.TransientModel):
    _name = "meeting.from.task"

    def create_new_meeting(self):
        active_id = self._context.get('active_ids')
        task_id = self.env['project.task'].browse(active_id)
        if task_id.meeting_id:
            raise ValidationError(_("This Task has already Meeting Assigned"))
        name = 'Meeting from : ' + str(task_id.name)
        meeting_id = self.env['calendar.event'].create(
            {'name': name,
             'start': self.starting_datetime,
             'stop': self.starting_datetime,
             'project_id': task_id.project_id and task_id.project_id.id or False,
             'task_id': task_id.id
             })
        task_id.meeting_id = meeting_id.id
    starting_datetime = fields.Datetime("Starting at", required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: