# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'All In One Task',
    'version': '17.0.1.2',
    'sequence': 1,
    'category': 'Generic Modules/Tools',
    'description':
        """
        This Module add below functionality into odoo

        All In One Task\n

    """,
    'summary': 'Dev Project Task dashboard',
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'depends': ['project','hr_timesheet','mail','crm','calendar'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/project_seq_view.xml',
        'data/task_seq_view.xml',
        'data/email_template_task_overdue_reminder.xml',
        'data/cron_task_overdue_reminder.xml',
        'data/cron_task_reminder.xml',
        'data/cron_task_timesheet_reminder_views.xml',
        'views/project_view.xml',
        'wizard/task_from_lead_view.xml',   
        'wizard/update_project.xml',
        'wizard/dev_mass_update_users.xml',
        'wizard/meeting_from_task_view.xml',
        'wizard/task_quick_edit.xml',
        'wizard/import_task_checklist_view.xml',
        'wizard/end_Task_view.xml',
        'report/template_task_report.xml',
        'report/menu_task_report.xml',
        'views/calendar_event_view.xml',
        'views/task_checklist_view.xml',
        'views/create_task_lead_view.xml',
        'views/task_view.xml',     
        'views/task_custom_fields.xml',
        'views/res_config_settings.xml',
        'views/task_template_view.xml',
        'views/dashboard.xml',
        ],
     'assets': {
        'web.assets_backend': [
            'dev_all_in_one_task/static/src/js/project_dashboard.js',
            'dev_all_in_one_task/static/src/js/chart_chart.js',
            'dev_all_in_one_task/static/src/css/dashboard_new.css',
            'dev_all_in_one_task/static/src/xml/project_dashboard_templates.xml',
        ]},
    
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
