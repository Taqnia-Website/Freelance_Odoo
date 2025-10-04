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
from odoo import fields, models,api,_
import pytz
from pytz import timezone
from pytz import utc

from datetime import datetime, date, timedelta
class task(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self,vals):
        vals['task_seq'] = self.env['ir.sequence'].next_by_code('task.sequence.code') or 'New'
        return super(task,self).create(vals)
        
    task_seq = fields.Char(string='Number', readonly=True)
    task_custom_lines = fields.One2many('task.custom.field.values', 't_id',
                                        string='Task Custom Fields')
    
    lead_id = fields.Many2one('crm.lead', 'Lead')
    task_priority = fields.Selection(selection=[('0', 'Normal'),
                                                   ('1', 'Good'),
                                                   ('2', 'Very Good'),
                                                   ('3', 'Excellent')],
                                        string="Priority")
#closing alert
    @api.constrains('stage_id')
    def _check_subtask_closing_status(self):
        print("self=================",self)
        for task_id in self:
            print("task_id====================",task_id.child_ids)
            if  task_id.child_ids:

                warn = False
                closing_stage_id = task_id.env.company and task_id.env.company.task_closing_stage_id or False
                if closing_stage_id and task_id.stage_id.id == closing_stage_id.id:
                    for sub_task_id in task_id.child_ids:
                        if sub_task_id.stage_id and sub_task_id.stage_id.id != closing_stage_id.id:
                            warn = True
                            break
                if warn:
                    raise ValidationError(_('''Some Sub-tasks are not closed yet. Close all sub-tasks in order to close this task'''))

#task auto assign
    def get_assign_user(self, stage, project_id):
        user_id = False
        assign_line_id = self.env['task.user.assignment'].search([('project_id', '=', project_id.id),
                                                                  ('stage_id', '=', stage)], limit=1)
        if assign_line_id:
            user_id = assign_line_id.user_id and assign_line_id.user_id or False
        return user_id



    @api.depends('checklist_ids')
    def _checklist_progress_status(self):
        for task in self:
            total_checklists = self.env['task.checklist'].search_count([])
            task_checklists = len(task.checklist_ids)
            progress = 0
            if total_checklists > 0:
                progress = (task_checklists * 100) / total_checklists
            task.checklist_progress = progress

    def fill_checklist_warning(self, checklists):
        warning = (_('''Below checklist must filled in order to move further'''))
        warning += (_('''\n\n'''))
        for checklist in checklists:
            warning += (_(''' - %s''') % (checklist.name))
            warning += (_('''\n'''))
        raise ValidationError(_(warning))



    checklist_ids = fields.Many2many('task.checklist', string='Checklists')
    checklist_progress = fields.Float(string='Checklist Progress', compute='_checklist_progress_status')

    def write(self, vals):
        # Handle user assignment based on stage_id
        project_id = self.project_id
        #if self.parent_id:
       #     project_id = self.display_project_id
        if 'stage_id' in vals and project_id:
            user_id = self.get_assign_user(vals['stage_id'], project_id)
            if user_id:
                user_list = self.user_ids.ids
                if user_id.id not in user_list:
                    user_list.append(user_id.id)
                vals.update({'user_ids': [(6, 0, user_list)]})

        # Handle checklist validation based on stage_id
        if 'stage_id' in vals:
            if vals['stage_id']:
                if self.stage_id:
                    required_checklist_ids = self.env['task.checklist'].search([('stage_id', '=', self.stage_id.id)])
                    if required_checklist_ids:
                        required = required_checklist_ids.ids
                        if 'checklist_ids' in vals:
                            filled = vals['checklist_ids']
                        else:
                            filled = self.checklist_ids.ids
                        if not all(checklist in filled for checklist in required):
                            self.fill_checklist_warning(required_checklist_ids)

        # Call the super method to perform the actual write operation
        result = super(task, self).write(vals)
        return result


#task meeting
    def copy(self, default=None):
        if default is None:
            default = {}
        default['meeting_id'] = False
        return super(project_task, self).copy(default)

    def action_view_meeting(self):
        meeting_id = self.env['calendar.event'].search(
            [('task_id', '=', self.id)], limit=1)
        if not meeting_id:
            raise ValidationError(_("There is no Meetings from this Task."))
        form_view = self.env.ref('calendar.view_calendar_event_form')
        return {
            'name': 'Meeting',
            'res_model': 'calendar.event',
            'res_id': meeting_id.id,
            'views': [(form_view.id, 'form')],
            'type': 'ir.actions.act_window',
        }

    meeting_id = fields.Many2one("calendar.event", string="Meeting")

#task overdue days
    @api.depends('date_end', 'stage_id.fold', 'date_deadline')
    def _compute_overdue_days(self):
        for rec in self:
            days = 0
            if rec.stage_id.fold and rec.date_end and rec.date_deadline:
                if rec.date_end.date() > rec.date_deadline.date():
                    difference = rec.date_end.date() - rec.date_deadline.date()
                    days = difference.days
            rec.overdue_days = days

    overdue_days = fields.Integer(string='Overdue Days', compute='_compute_overdue_days')

#task reminder
    def send_deadline_reminder_emails(self, employee, table):
        email_body = ''
        email_body += '''<b>Hello, ''' + employee.name + \
                      '''</b><br/><br/><h3>Following Tasks's deadline is near, \
                      please pay attention:</h3><br/>'''
        email_body += table
        email_id = self.env['mail.mail'].create(
            {'subject': 'Task Deadline Reminder',
             'email_from': employee.user_id.company_id.email,
             'email_to': employee.work_email,
             'message_type': 'email',
             'body_html': email_body})
        email_id.send()

    def _prepare_email_format(self, reminder_users, reminder_tasks):
        for user in reminder_users:
            table = ''
            table += ''' <table border=1 width=100%>
                            <tr>
                                <td width="20%">
                                    <center><b>Task</b></center>
                                </td>
                                <td width="40%">
                                    <center><b>Project</b></center>
                                </td>
                                <td width="12%">
                                    <center><b>Deadline</b></center>
                                </td>
                                <td width="13%">
                                    <center><b>Progress</b></center>
                                </td>
                            </tr>'''
            employee_id = self.env['hr.employee'].search(
                [('user_id', '=', user)], limit=1)
            if employee_id:
                tasks = self.env['project.task'].search(
                    [('id', 'in', reminder_tasks),
                     ('user_ids', 'in', user)])
                if tasks:
                    for task in tasks:
                        #deadline = datetime.strptime\
                          #  (str(task.date_deadline), "%Y-%m-%d").\
                         #   strftime('%d-%m-%Y')
                        deadline = datetime.strptime(str(task.date_deadline), "%Y-%m-%d %H:%M:%S").strftime('%d-%m-%Y')                        
                        project = \
                            task.project_id and task.project_id.name or ''
                        progress = str(task.progress) + ' ' + '%'
                        table += \
                            '<tr>' + '<td>' + task.name + '</td>' + '<td>' + \
                            project + '</td>' + \
                            '<td style="text-align: center;">' + str(deadline) \
                            + '</td>' + '<td style="text-align: center;">' \
                            + progress + '</td>' + '</tr>'
                    table += '''</table>'''
                    self.send_deadline_reminder_emails(employee_id, table)

    def task_reminder(self):
        tasks = self.env['project.task'].search([])
        first_reminder_tasks = []
        first_reminder_users = []
        second_reminder_users = []
        second_reminder_tasks = []
        for task in tasks:
            
            if task.send_reminders and task.date_deadline and task.user_ids:
                print ("caca========",task.send_reminders)
                first_reminder = self.env.company.first_reminder
                second_reminder = self.env.company.second_reminder
                #deadline_date = datetime.strptime(str(task.date_deadline), '%Y-%m-%d').date()
                deadline_datetime = datetime.strptime(str(task.date_deadline), '%Y-%m-%d %H:%M:%S')
                deadline_date = deadline_datetime.date()
                
                if first_reminder > 0:
                    print ("1========",first_reminder)
                    first_reminder_date = deadline_date - timedelta(
                        days=first_reminder)
                    print ("remin========",first_reminder_date)
                    print ("date========",date.today())
                    if first_reminder_date == date.today():
                        first_reminder_tasks.append(int(task.id))
                        for task_user_id in task.user_ids:
                            first_reminder_users.append(int(task_user_id.id))
                if second_reminder > 0:
                    
                    second_reminder_date = deadline_date - timedelta(
                        days=second_reminder)
                    if second_reminder_date == date.today():
                        second_reminder_tasks.append(int(task.id))
                        for task_user_id in task.user_ids:
                            second_reminder_users.append(int(task_user_id.id))
        if first_reminder_users:
            first_reminder_users = list(set(first_reminder_users))
            self._prepare_email_format(first_reminder_users,
                                       first_reminder_tasks)
        if second_reminder_users:
            second_reminder_users = list(set(second_reminder_users))
            self._prepare_email_format(second_reminder_users,
                                       second_reminder_tasks)

    send_reminders = fields.Boolean(string="Send Reminder Email")

#send by mail
    #def get_task_deadline(self):
     #   deadline = ''
    #    if self.date_deadline:
      #      offset = datetime.now(pytz.timezone(self.env.user.tz or 'UTC')).utcoffset()
    # #       deadline = fields.Datetime.to_string(datetime.strptime(str(self.date_deadline), "%Y-%m-%d %H:%M:%S") + offset)
    #    return str(deadline)

    def get_task_deadline(self):
        deadline = ''
        if self.date_deadline:
            offset = datetime.now(pytz.timezone(self.env.user.tz or 'UTC')).utcoffset()
            deadline_str = str(self.date_deadline).split(".")[0]
            deadline = fields.Datetime.to_string(datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S") + offset)
        return str(deadline)



    def task_send_by_mail(self):
        ir_model_data = self.env['ir.model.data']
        template_id = self.env.ref('dev_all_in_one_task.template_dev_task_send_by_mail')
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
            
        except ValueError:
            compose_form_id = False
        if self.user_ids and template_id:
            partners = ''
            for user_id in self.user_ids:
                if user_id.partner_id and user_id.partner_id.id:
                    partners += ', ' + str(user_id.partner_id.id)
            if partners:
                template_id.partner_to = partners
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'project.task',
            'active_model': 'project.task',
            'active_id': self.ids[0],
            'default_res_ids': self.ids,
            'default_template_id': template_id and template_id.id or False,
            'default_composition_mode': 'comment',
            'force_email': True,
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
#tasktimer log
    task_start_date = fields.Datetime("Task Start Date")

    def start_task(self):
        current_time = datetime.now()
        self.task_start_date = current_time
        return True

    def end_task(self):
        start_time = self.task_start_date
        current_time = datetime.now()
        final_time = current_time - start_time
        duration = str(str(final_time).split(':')[0]) + ':' + str(final_time).split(':')[1]

        task_wizard = self.env['end.task.wizard'].create({'task_start_date': self.task_start_date,
                                                          'duration': duration, 'description': ' '})
        return {
            'view_mode': 'form',
            'res_id': task_wizard.id,
            'res_model': 'end.task.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
#timesheet reminder

    def send_timesheet_reminder(self):
        print("self========================",self)
        task_ids = self.search([('user_ids', '!=', False),
                                ('project_id', '!=', False),
                                ('allocated_hours', '>', 0)])

        if task_ids:
            template_id = self.env.ref('dev_all_in_one_task.email_template_timesheet_reminder')
            if template_id:
                for task in task_ids:
                    for user in task.user_ids:
                        if user.partner_id and user.partner_id.email:
                            if task.effective_hours < task.allocated_hours:
                                template_id.write({'partner_to': user.partner_id.id})
                                template_id.send_mail(task.id, force_send=True)
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
