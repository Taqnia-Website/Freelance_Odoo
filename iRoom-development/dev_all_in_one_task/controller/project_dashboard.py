# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Mruthul Raj @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
# import datetime
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _
from operator import itemgetter
import itertools
import operator
from datetime import date,datetime,timedelta
# from datetime import datetime
from itertools import groupby
import base64


class ProjectFilter(http.Controller):
    """The ProjectFilter class provides the filter option to the js.
    When applying the filter returns the corresponding data."""

    @http.route('/all_project_filter', auth='public', type='json')
    def all_project_filter(self):
        
        user_list = []
        partner_list = []
        project_list = []
        
        user_ids = request.env['res.users'].search([("share", "=", False)])
        partner_ids = request.env['res.partner'].search([])
        project_ids = request.env['project.project'].search([])
       
        for user_id in user_ids:
            dic = {'name': user_id.name,
                   'id': user_id.id}
            user_list.append(dic)
        for partner_id in partner_ids:
            dic = {'name': partner_id.name,
                   'id': partner_id.id}
            partner_list.append(dic)
        for project_id in project_ids:
            dic = {'name': project_id.name,
                   'id': project_id.id}
            project_list.append(dic)
          
        return [user_list,partner_list,project_list]   
    
    @http.route('/get/project/tiles/data', auth='public', type='json')
    def get_project_tiles_data(self, **kwargs):
        
        today = date.today()
                            
        task_domain = []
        overdue_domain = []
        project_domain = []
        
        if not kwargs.get('duration'):
            task_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
            overdue_domain = [('date_deadline', '<', today)]
            project_domain = [('date', '>=', today),('date', '<=', today)]
        if kwargs:
            if kwargs['user_id']:
                if kwargs['user_id'] != 'all':
                    user_id = int(kwargs['user_id'])
                    task_domain += [('user_ids','=',user_id)]
                    overdue_domain += [('user_ids','=',user_id)]
                    project_domain += [('user_id','=',user_id)]
            if kwargs['partner_id']:
                if kwargs['partner_id'] != 'all':
                    partner_id = int(kwargs['partner_id'])
                    task_domain += [('partner_id','=',partner_id)]
                    overdue_domain += [('partner_id','=',partner_id)]
                    project_domain += [('partner_id','=',partner_id)]
            if kwargs['project_id']:
                if kwargs['project_id'] != 'all':
                    project_id = int(kwargs['project_id'])
                    task_domain += [('project_id','=',project_id)]
                    overdue_domain += [('project_id','=',project_id)]
                    project_domain += [('id','=',project_id)]
            if kwargs['duration']:
                duration = kwargs['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today  - timedelta(days=duration)
                    task_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]
                    overdue_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<', today)]
                    project_domain += [('date', '>=', filter_date), ('date', '<=', today)]
                if duration == "all":
                    overdue_domain += [('date_deadline', '<', today)]
        if kwargs.get('duration') == "0":
            overdue_domain = [('date_deadline', '<', today)]

        uid = request.env.user.id
        total_task_data = request.env['project.task'].search([('user_ids', 'in', uid)] + task_domain)
        total_project_data = request.env['project.project'].search(project_domain)
        active_task_data = request.env['project.task'].search(task_domain)
        myoverdue_task_data = request.env['project.task'].search([('user_ids', 'in', uid)] + overdue_domain)
        overdue_task_data = request.env['project.task'].search(overdue_domain)
        today_task = request.env['project.task'].search(task_domain)

        today_task_data = []

        for task in today_task:
            # Ensure date_deadline exists and is a valid datetime
            if task.date_deadline:
                task_date = task.date_deadline.date()
                if task_date == today:
                    today_task_data.append(task)
        
        user_name = request.env.user.name
        user_img = request.env.user.image_1920

        return {
            'total_task_data': total_task_data.ids,
            'total_project_data': total_project_data.ids,
            'active_task_data': active_task_data.ids,
            'myoverdue_task_data': myoverdue_task_data.ids,
            'overdue_task_data': overdue_task_data.ids,
            'today_task_data': [task.id for task in today_task_data],
            
            'user_img': user_img,
            'user_name': user_name
        }
    
    # ======1111 project task 1111===================
    @http.route('/task/project/chart/data', auth='public', type='json')
    def get_task_project_chart_data(self, **kw):
        all_color_list = ['rgba(186, 224, 137, 0.9)','rgba(79, 75, 71, 0.5)','rgba(237, 119, 95, 0.6)','rgba(199, 192, 133, 0.9)',
                        'rgba(140, 185, 230, 0.5)','rgba(230, 140, 189, 0.8)','rgba(14, 144, 148, 0.4)','rgba(254, 94, 178, 0.5)',
                        'rgba(95, 247, 252 , 0.5)','rgba(255, 99, 71, 0.4','rgba(148, 39, 14, 0.4)','rgba(149, 156, 158, 0.4)',
                        'rgba(69, 80, 82, 0.4)','rgba(224, 5, 52, 0.4)','rgba(90, 120, 232, 0.4)','rgba(189, 90, 232, 0.4)',
                        'rgba(240, 128, 128, 0.3)','rgba(241, 181, 31, 0.7)', 'rgba(136, 67, 149, 0.3)','rgba(240, 128, 128, 0.2)']

        today = date.today()
        data = kw['data']

        task_domain = []
                
        if not data.get('duration'):
            task_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    task_domain += [('user_ids','=',user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    task_domain += [('partner_id','=',partner_id)]
            if data['project_id']:
                if data['project_id'] != 'all':
                    project_id = int(data['project_id'])
                    task_domain += [('project_id','=',project_id)]
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today  - timedelta(days=duration)
                    task_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]
                    
        uid = request.env.user.id
        repeated_project = []
        repeated_project_chart = []
        project_task_repeat_time = []

        # Fetch project task data with project_id and name
        project_task = request.env['project.task'].search_read(task_domain, fields=['project_id', 'name', 'id'])

        # Sorting by project_id, handling None values
        n_lines = sorted(project_task, key=lambda x: x['project_id'][0] if x['project_id'] else float('inf'))

        groups = itertools.groupby(n_lines, key=operator.itemgetter('project_id'))
        lines = [{'project_id': k, 'values': [x for x in v]} for k, v in groups if k] #filter out None project_id groups

        project_ids_lst = []
        for x in lines:
            project_id_lst = []
            for id in x['values']:
                project_id_lst.append(id['id'])
            project_ids_lst.append(project_id_lst)

        project_ids_lst = sorted(project_ids_lst, key=lambda x: len(x), reverse=True)

        for line in lines:
            repeated_project.append(
                {'project': line.get('project_id')[1], 'repeated_time': len(line.get('values'))})

        repeated_project = sorted(repeated_project, key=lambda i: i['repeated_time'], reverse=True)

        for rep_customer_data in repeated_project:
            repeated_project_chart.append(rep_customer_data.get('project'))
            project_task_repeat_time.append(rep_customer_data.get('repeated_time'))

       
        project_chart_data = {
            'labels': repeated_project_chart,
            'datasets': [{
                'label': "Total Projects",
                'backgroundColor': all_color_list[:len(repeated_project_chart)],
                'data': project_task_repeat_time,
                'detail': project_ids_lst
            }]
        }
        return{
            'project_chart_data': project_chart_data
        }
    
    # ======22 Task Stages 22===================
    @http.route('/task/stages/chart/data', auth='public', type='json')
    def get_task_stages_chart_data(self, **kw):
        all_color_list = ['rgba(136, 67, 149, 0.4)','rgba(217, 254, 67, 0.8)','rgba(140, 120, 5, 0.6)','rgba(240, 128, 128, 0.6)',
                        'rgba(139, 134, 243, 0.6)','rgba(241, 181, 31, 0.8)','rgba(14, 144, 148, 0.4)','rgba(254, 94, 178, 0.5)',
                        'rgba(95, 247, 252 , 0.5)','rgba(255, 99, 71, 0.4','rgba(148, 39, 14, 0.4)','rgba(149, 156, 158, 0.4)',
                        'rgba(69, 80, 82, 0.4)','rgba(224, 5, 52, 0.4)','rgba(90, 120, 232, 0.4)','rgba(189, 90, 232, 0.4)',
                        'rgba(240, 128, 128, 0.3)','rgba(241, 181, 31, 0.7)', 'rgba(136, 67, 149, 0.3)','rgba(240, 128, 128, 0.2)']

        today = date.today()
        data = kw['data']

        task_domain = []
                
        if not data.get('duration'):
            task_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    task_domain += [('user_ids','=',user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    task_domain += [('partner_id','=',partner_id)]
            if data['project_id']:
                if data['project_id'] != 'all':
                    project_id = int(data['project_id'])
                    task_domain += [('project_id','=',project_id)]
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today  - timedelta(days=duration)
                    task_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]
        uid = request.env.user.id
        repeated_stages = []
        repeated_stages_chart = []
        stages_task_repeat_time = []

        # Fetch project task data with project_id and name
        project_task = request.env['project.task'].search_read(task_domain, fields=['stage_id', 'name', 'id'])

        # Sorting by project_id, handling None values
        n_lines = sorted(project_task, key=lambda x: x['stage_id'][0] if x['stage_id'] else float('inf'))

        groups = itertools.groupby(n_lines, key=operator.itemgetter('stage_id'))
        lines = [{'stage_id': k, 'values': [x for x in v]} for k, v in groups if k] #filter out None project_id groups

        stage_ids_lst = []
        for x in lines:
            stage_id_lst = []
            for id in x['values']:
                stage_id_lst.append(id['id'])
            stage_ids_lst.append(stage_id_lst)

        stage_ids_lst = sorted(stage_ids_lst, key=lambda x: len(x), reverse=True)

        for line in lines:
            repeated_stages.append(
                {'stage': line.get('stage_id')[1], 'repeated_time': len(line.get('values'))})

        repeated_stages = sorted(repeated_stages, key=lambda i: i['repeated_time'], reverse=True)

        for rep_customer_data in repeated_stages:
            repeated_stages_chart.append(rep_customer_data.get('stage'))
            stages_task_repeat_time.append(rep_customer_data.get('repeated_time'))

       
        stages_chart_data = {
            'labels': repeated_stages_chart,
            'datasets': [{
                'label': "Total Stages",
                'backgroundColor': all_color_list[:len(repeated_stages_chart)],
                'data': stages_task_repeat_time,
                'detail': stage_ids_lst
            }]
        }
        return{
            'stages_chart_data': stages_chart_data
        }
    
    # ======33 deadline 33===================
    @http.route('/task/deadline/chart/data', auth='public', type='json')
    def get_task_deadline_chart_data(self, **kw):
        all_color_list = ['rgba(156, 140, 184,0.5)', 'rgba(247, 228, 99, 0.8)', 'rgba(216, 148, 224, 0.6)']

        today = date.today()
        data = kw['data']

        task_domain = []
                
        if not data.get('duration'):
            task_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    task_domain += [('user_ids','=',user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    task_domain += [('partner_id','=',partner_id)]
            if data['project_id']:
                if data['project_id'] != 'all':
                    project_id = int(data['project_id'])
                    task_domain += [('project_id','=',project_id)]
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today  - timedelta(days=duration)
                    task_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]  # Get the date part only

        overdue_count = 0
        today_count = 0
        upcoming_count = 0

        # Fetch all project tasks with deadline information
        project_tasks = request.env['project.task'].search(task_domain)  # Only tasks with deadlines

        # Initialize lists to store task IDs for each category
        overdue_task_ids = []
        today_task_ids = []
        upcoming_task_ids = []

        for task in project_tasks:
            deadline = task.date_deadline
            if deadline:
            
                if deadline.date() < today:
                    overdue_count += 1
                    overdue_task_ids.append(task.id)
                if deadline.date() == today:
                    today_count += 1
                    today_task_ids.append(task.id)
                elif deadline.date() > today:
                    upcoming_count += 1
                    upcoming_task_ids.append(task.id)
            
        # Update the chart data to show raw counts instead of percentages
        task_deadline_chart_data = {
            'labels': ['Overdue','Today' , 'Upcoming'],
            'datasets': [{
                'label': "Task Deadlines",
                'data': [overdue_count, today_count, upcoming_count],  # Raw counts instead of percentages
                'backgroundColor': all_color_list,  # Colors matching the image
                'detail': [overdue_task_ids, today_task_ids, upcoming_task_ids],  # Add task IDs
            }]
        }
        

        return {
            'task_deadline_chart_data': task_deadline_chart_data
        }
    

    # ======44 timesheet hours44========    
    @http.route('/timesheet/hours/chart/data', auth='public', type='json')
    def get_timesheet_hours_chart_data(self, **kw):
        
        today = date.today()
        data = kw['data']

        # task_domain = []
                
        # if not data.get('duration'):
        #     task_domain = [('date', '>=', today),('date', '<=', today)]
        # if data:
        #     if data['user_id']:
        #         if data['user_id'] != 'all':
        #             user_id = int(data['user_id'])
        #             task_domain += [('user_id','=',user_id)]
        #     if data['project_id']:
        #         if data['project_id'] != 'all':
        #             project_id = int(data['project_id'])
        #             task_domain += [('project_id','=',project_id)]
        #     if data['duration']:
        #         duration = data['duration']
        #         if duration != "all":
        #             duration = int(duration)
        #             filter_date = today  - timedelta(days=duration)
        #             task_domain += [('date', '>=', filter_date), ('date', '<=', today)]
        
        first_day = today.replace(day=1)
        last_day = (first_day.replace(month=first_day.month + 1) - timedelta(days=1))

        # Generate the dates for the month
        dates = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
        date_strings = [date.strftime('%d %b') for date in dates]

        # Initialize hours data with 0 and timesheet IDs for each day
        hours = [0] * len(dates)
        timesheet_ids_by_day = [[] for _ in range(len(dates))]  # List to store IDs for each day

        # Fetch timesheet lines for the current month
        timesheet_lines = request.env['account.analytic.line'].search([('date', '>=', first_day),('date', '<=', last_day)] )

        # Aggregate hours and store timesheet IDs for each day
        for line in timesheet_lines:
            day_index = (line.date - first_day).days
            if 0 <= day_index < len(hours):
                hours[day_index] += line.unit_amount 
                timesheet_ids_by_day[day_index].append(line.id) # Store Timesheet ID

        # Create the chart data structure
        timesheet_chart_data = {
            'labels': date_strings,
            'datasets': [{
                'label': "Timesheet Hours",
                'data': hours,
                'borderColor': 'blue',
                'fill': True,
                'pointBackgroundColor': 'white',
                'detail': timesheet_ids_by_day,  # Add the timesheet IDs
            }]
            
        }

        return {
            'timesheet_chart_data': timesheet_chart_data
        }
    
    # ==========55 task priority 55===============
    @http.route('/task/priority/chart/data', auth='public', type='json')
    def get_task_priority_chart_data(self, **kw):
        all_color_list = ['rgba(157, 206, 235, 0.9)','rgba(242, 172, 206, 0.9)']
        today = date.today()
        data = kw['data']

        task_domain = []
                
        if not data.get('duration'):
            task_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    task_domain += [('user_ids','=',user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    task_domain += [('partner_id','=',partner_id)]
            if data['project_id']:
                if data['project_id'] != 'all':
                    project_id = int(data['project_id'])
                    task_domain += [('project_id','=',project_id)]
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today  - timedelta(days=duration)
                    task_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]

        low = []
        high = []
        priority_data = request.env['project.task'].search(task_domain)
        for p_data in priority_data:
            if p_data.priority == '0':
                low.append(p_data['id'])
            if p_data.priority == '1':
                high.append(p_data['id'])
            
        
        priority_label = ['Low','High']
        priority_value = [len(low),len(high)]
        priority_counting_ids = [low,high]

        task_priority_chart_data = {
            'labels': priority_label,
            'datasets': [{
                'label': "Priority",
                'backgroundColor': all_color_list[:len(priority_label)],
                'data': priority_value,
                'detail' : priority_counting_ids
            }]
        }
        return {
            'task_priority_chart_data': task_priority_chart_data,
        }

    
    # ========table new task=================
    @http.route('/project/table/data', auth='public', type='json')
    def get_task_list_data(self, **kw):
        data=kw['data']
        today = date.today()
        data = kw['data']

        task_domain = []
        activity_domain = []
                
        if not data.get('duration'):
            task_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
            activity_domain = [('date_deadline', '>=', today),('date_deadline', '<=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    task_domain += [('user_ids','=',user_id)]
                    activity_domain += [('user_id','=',user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    task_domain += [('partner_id','=',partner_id)]
            if data['project_id']:
                if data['project_id'] != 'all':
                    project_id = int(data['project_id'])
                    task_domain += [('project_id','=',project_id)]
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today  - timedelta(days=duration)
                    task_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]
                    activity_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '<=', today)]

        low = []
        high = []                
        new_task_list = request.env['project.task'].search_read(task_domain ,fields=['name','project_id','priority','date_deadline'],
                                                                            order="date_deadline Asc")
                     
        for task in new_task_list:
            if task['priority'] == '0':
                task['priority_display'] = 'Low'
            elif task['priority'] == '1':
                task['priority_display'] = 'High'
            else:
                task['priority_display'] = '-' # Handle cases where priority isn't 0 or 1.
            
            #remove original priority value, so it wont display on table
            del task['priority']

        activity_task_list = request.env['mail.activity'].search_read([ ('res_model', '=', 'project.task')] + activity_domain,
                                                                      fields=['res_name', 'activity_type_id', 'summary','date_deadline'],
                                                                       order="date_deadline desc")
        
        for activity in activity_task_list:
            if activity['date_deadline']:
                # Convert the date to the required format directly using strftime
                original_date = activity['date_deadline']
                formatted_date = original_date.strftime('%d-%m-%Y')  # directly formatting the date object
                activity['date_deadline'] = formatted_date

        view_name = 'mail.activity.view.form'  # Replace with your view name
        view = request.env['ir.ui.view'].search([('name', '=', view_name)], limit=1)             

        return{
            'new_task_list': new_task_list,
            'activity_task_list': activity_task_list,
            'view_id' : view.id or None
            
        }

    @http.route('/project/filter-apply', auth='public', type='json')
    def project_filter_apply(self, **kw):
        data = kw['data']
        
        user_id = data['pruser']
        partner_id = data['prpartner']
        project_id = data['prproject']
        duration = data['prduration']

        result = self.get_project_tiles_data(user_id=user_id, partner_id=partner_id, project_id=project_id, duration=duration)
        return result    
        