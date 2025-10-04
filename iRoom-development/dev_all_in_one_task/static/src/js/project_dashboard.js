/** @odoo-module */

import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
const { Component, onWillStart, onMounted, useState, useRef } = owl
import { useService } from "@web/core/utils/hooks";
import { jsonrpc } from "@web/core/network/rpc_service";
// import { rpc } from "@web/core/network/rpc";
 import { _t } from "@web/core/l10n/translation";
export class ProjectDashboard extends Component {

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.rpc = this.env.services.rpc
        this.state = useState({
            rowsPerPage: 5,
            currentPage:1,
            totalrows: 0,
            currentprPage:1,
            totalprrows: 0,
            currentrecPage:1,
            totalrecrows: 0,
            currentdelPage:1,
            totaldelrows: 0,
            top_moving_chart: null,
            view_id: null,
       
            company_currency: ' '
        })
        
        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
    }

    async onWillStart() {
       await this.fetch_project_data();
       await this.getGreetings()
       await loadJS("https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js")
    }

    async onMounted() {
       this.render_project_filter();
       this._onchangeProjectTaskChart();
       this._onchangeStagesTaskChart();
       this._onchangeDeadlineChart();
       this._onchangeHoursChart();
       this._onchangeTaskPriorityChart();
       this.render_task_table_data(this.state.rowsPerPage, this.state.currentrecPage);
       this.render_activity_table_data(this.state.rowsPerPage, this.state.currentdelPage);
    }

    async getGreetings() {
        var self = this;
        const now = new Date();
        const hours = now.getHours();
        if (hours >= 5 && hours < 12) {
            self.greetings = "Good Morning";
        }
        else if (hours >= 12 && hours < 18) {
            self.greetings = "Good Afternoon";
        }
        else {
            self.greetings = "Good Evening";
        }
    }

    downloadReport(e) {
        e.stopPropagation();
        e.preventDefault();

        var opt = {
            margin: 1,
            filename: 'ProjectDashboard.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'px', format: [1920, 1080], orientation: 'landscape' }
        };
        html2pdf().set(opt).from(document.getElementById("dashboard")).save()

    }

    _downloadChart(e) {
        var chartId = e.target.id.slice(0, e.target.id.length - 4)
        var chartEle = document.querySelector("#" + chartId)
        const imageDataURL = chartEle.toDataURL('image/png'); // Generate image data URL
        const filename = chartId + 'ProjectDashboard.png'; // Set your preferred filename
        const link = document.createElement('a');
        link.href = imageDataURL;
        link.download = filename;
        link.click();
    }

    // =====filters======
    
    render_project_filter() {
        jsonrpc('/all_project_filter').then(function (data) {
            var users = data[0]
            var partners = data[1]
            var projects = data[2]
            var durations=data[3]

            $(users).each(function (user) {
                $('#pruser_selection').append("<option value=" + users[user].id + ">" + users[user].name + "</option>");
            });
            $(partners).each(function (partner) {
                $('#prpartner_selection').append("<option value=" + partners[partner].id + ">" + partners[partner].name + "</option>");
            });
            $(projects).each(function (project) {
                $('#prproject_selection').append("<option value=" + projects[project].id + ">" + projects[project].name + "</option>");
            });
         })
    }

    _onchangeProjectFilter(ev) {
        this.flag = 1

	    var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        
        this._onchangeProjectTaskChart();
        this._onchangeStagesTaskChart();
        this._onchangeDeadlineChart();
        this._onchangeHoursChart();
        this._onchangeTaskPriorityChart();
        this.render_task_table_data(this.state.rowsPerPage, this.state.currentrecPage);
        this.render_activity_table_data(this.state.rowsPerPage, this.state.currentdelPage);
        var self = this;
        
        jsonrpc('/project/filter-apply', {
            'data': {
                
                'pruser': pruser_selection,
                'prpartner': prpartner_selection,
                'prproject': prproject_selection,
                'prduration': duration_selection,
            }
        }).then(function (data) {

            		    // count box click that time pass data
            self.total_task_data = data['total_task_data']
            self.total_project_data = data['total_project_data']
            self.active_task_data = data['active_task_data']
            self.myoverdue_task_data = data['myoverdue_task_data']
            self.overdue_task_data = data['overdue_task_data']
            self.today_task_data = data['today_task_data']
            
            
            			// after change value display on xml side count
            document.querySelector('#total_task_data').innerHTML = data['total_task_data'].length;
            document.querySelector('#total_project_data').innerHTML = data['total_project_data'].length;
            document.querySelector('#active_task_data').innerHTML = data['active_task_data'].length;
            document.querySelector('#myoverdue_task_data').innerHTML = data['myoverdue_task_data'].length;
            document.querySelector('#overdue_task_data').innerHTML = data['overdue_task_data'].length;
            document.querySelector('#today_task_data').innerHTML = data['today_task_data'].length;
            

        })
    }

      // counters-------------------------------

    // async fetch_project_data() 
    // {
    //     this.flag = 0
    //     var self = this;
    //     const result = await rpc('/get/project/tiles/data');
            // self.total_task_data = result['total_task_data']
            // self.total_project_data = result['total_project_data']
            // self.active_task_data = result['active_task_data']
            // self.myoverdue_task_data = result['myoverdue_task_data']
            // self.overdue_task_data = result['overdue_task_data']
            // self.today_task_data = result['today_task_data']
            
            // self.user_name = result['user_name']
            // self.user_img = result['user_img']
    //     return result;
    // }
    fetch_project_data() 
    {
        this.flag = 0
        var self = this;
        var def1 = jsonrpc('/get/project/tiles/data').then(function (result) 
       
        {
            self.total_task_data = result['total_task_data']
            self.total_project_data = result['total_project_data']
            self.active_task_data = result['active_task_data']
            self.myoverdue_task_data = result['myoverdue_task_data']
            self.overdue_task_data = result['overdue_task_data']
            self.today_task_data = result['today_task_data']
            self.user_name = result['user_name']
            self.user_img = result['user_img']
        });
        return $.when(def1);
    }


    action_total_task(e) {
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var rec_id = e.currentTarget.getAttribute('rec-id');
        var action = e.currentTarget.id || false;
    
        var domain = false;

        if (action == 'total_task_data1') {
            domain = [["id", "in", this.total_task_data]];
        }else if (action == 'active_task_data1') {
            domain = [["id", "in", this.active_task_data]]
        }else if (action == 'myoverdue_task_data1') {
            domain = [["id", "in", this.myoverdue_task_data]]
        }else if (action == 'overdue_task_data1') {
            domain = [["id", "in", this.overdue_task_data]]
        }else if (action == 'today_task_data1') {
            domain = [["id", "in", this.today_task_data]]
        }else if (rec_id != 'undefined') {
            domain = [["id", "=", rec_id]]
        }
    
        this.action.doAction({
            name: _t(" Total Task"),
            type: 'ir.actions.act_window',
            res_model: 'project.task',
            domain: domain,
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            target: 'current'
        }, options)
        
    }

    action_total_project(e) {
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var rec_id = e.currentTarget.getAttribute('rec-id');
        var action = e.currentTarget.id || false;
    
        var domain = false;

        if (action == 'total_project_data1') {
            domain = [["id", "in", this.total_project_data]];
        // }else if (action == 'order_due_shipment_data1') {
        //     domain = [["id", "in", this.order_due_shipment_data]]
        }else if (rec_id != 'undefined') {
            domain = [["id", "=", rec_id]]
        }
    
        this.action.doAction({
            name: _t(" Total Projects"),
            type: 'ir.actions.act_window',
            res_model: 'project.project',
            domain: domain,
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            target: 'current'
        }, options)
        
    }

    // ========11 project task chart 111===========
    async _onchangeProjectTaskChart(ev)
    {
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        
        var self = this;
        await jsonrpc("/task/project/chart/data",
        {
        'data':
            {
                'user_id': pruser_selection,
                'partner_id': prpartner_selection, 
                'project_id': prproject_selection,
                'duration':duration_selection,   
            }
        }).then(function (data)
        {
            var ctx = document.querySelector("#project_chart_data");
            new Chart(ctx, {
                type: 'bar',
                data: data.project_chart_data,
                options: {
                    maintainAspectRatio: false,
                
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.project_chart_data.labels[clickedIndex];
                            const clickedValue = data.project_chart_data.datasets[0].detail[clickedIndex]
                            var options = {
                            };
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options)
                        } else {
                        }
                    }
                }
            });
        });
    }

    // ========22 stages chart===========
    async _onchangeStagesTaskChart(ev)
    {
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        
        var self = this;
        await jsonrpc("/task/stages/chart/data",
        {
        'data':
            {
                'user_id': pruser_selection,
                'partner_id': prpartner_selection, 
                'project_id': prproject_selection,
                'duration':duration_selection,    
            }
        }).then(function (data)
        {
            var ctx = document.querySelector("#stages_chart_data");
            new Chart(ctx, {
                type: 'doughnut',
                data: data.stages_chart_data,
                options: {
                    maintainAspectRatio: false,
                
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.stages_chart_data.labels[clickedIndex];
                            const clickedValue = data.stages_chart_data.datasets[0].detail[clickedIndex]
                            var options = {
                            };
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options)
                        } else {
                        }
                    }
                }
            });
        });
    }

    // ========33 deadline chart===========
    async _onchangeDeadlineChart(ev)
    {
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        
        var self = this;
        await jsonrpc("/task/deadline/chart/data",
        {
        'data':
            {
                'user_id': pruser_selection,
                'partner_id': prpartner_selection, 
                'project_id': prproject_selection,
                'duration':duration_selection,  
            }
        }).then(function (data)
        {
            var ctx = document.querySelector("#task_deadline_chart_data");
            new Chart(ctx, {
                type: 'pie',
                data: data.task_deadline_chart_data,
                options: {
                    maintainAspectRatio: false,
                
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.task_deadline_chart_data.labels[clickedIndex];
                            const clickedValue = data.task_deadline_chart_data.datasets[0].detail[clickedIndex]
                            var options = {
                            };
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options)
                        } else {
                        }
                    }
                }
            });
        });
    }

    // ========44 month chart===========
    async _onchangeHoursChart(ev)
    {
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        
        var self = this;
        await jsonrpc("/timesheet/hours/chart/data",
        {
        'data':
            {
                'user_id': pruser_selection,
                'partner_id': prpartner_selection, 
                'project_id': prproject_selection,
                'duration':duration_selection,    
            }
        }).then(function (data)
        {
            var ctx = document.querySelector("#timesheet_chart_data");
            
            new Chart(ctx, {
                type: 'line',
                data: data.timesheet_chart_data,
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            // title: {
                            //     display: true,
                            //     text: 'Hours'
                            // },
                            ticks: {
                                callback: function(value, index, values) {
                                    return value + ' hrs';
                                }
                            }
                        }
                    },
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedValue = data.timesheet_chart_data.datasets[0].detail[clickedIndex]; // Timesheet IDs
                            var options = {};
                            self.action.doAction({
                                name: _t('Timesheet Entries'), // Customize the action name
                                type: 'ir.actions.act_window',
                                res_model: 'account.analytic.line', // Use the correct model
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options);
                        } else {
                            // Handle click if no data point is clicked
                        }
                    }
                }
            });
        });
    }

    // ======55 task priortiy55===========
    async _onchangeTaskPriorityChart(ev){
        
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;

        var self = this;
        await jsonrpc("/task/priority/chart/data",
        {
        'data':
            {
                
                'user_id': pruser_selection,
                'partner_id': prpartner_selection, 
                'project_id': prproject_selection,
                'duration':duration_selection, 
            }
        }).then(function (data)

       {
    var ctx = document.querySelector("#task_priority_chart_data");

    // ✅ Destroy old chart instance if exists
    if (ctx.chartInstance) {
        ctx.chartInstance.destroy();
    }

    // ✅ Create new chart and save reference
    ctx.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: data.task_priority_chart_data,
        options: {
            maintainAspectRatio: false,
            onClick: (evt, elements) => {
                if (elements.length > 0) {
                    const element = elements[0];
                    const clickedIndex = element.index;
                    const clickedLabel = data.task_priority_chart_data.labels[clickedIndex];
                    const clickedValue = data.task_priority_chart_data.datasets[0].detail[clickedIndex];
                    console.log("Clicked label:", clickedLabel, "Clicked value:", clickedValue);

                    var options = {};

                    self.action.doAction({
                        name: _t(clickedLabel),
                        type: 'ir.actions.act_window',
                        res_model: 'project.task',
                        domain: [["id", "in", clickedValue]],
                        view_mode: 'list,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    }, options);
                } else {
                    console.log("Click outside chart area");
                }
            }
        }
    });
});

    }


    // ========task table 111==============
    
    async render_task_table_data(rowsPerPage, page) {
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        var self = this;
        
        await jsonrpc("/project/table/data", {
            'data': {
                    'user_id': pruser_selection,
                    'partner_id': prpartner_selection, 
                    'project_id': prproject_selection,
                    'duration':duration_selection, 
                }
        }).then(function (data) {
            var new_task_list = data['new_task_list'];
            self.state.totalrecrows = new_task_list.length;
            var tbody = document.querySelector("#my_table_new_task_list tbody");
            tbody.innerHTML = '';
    
            const start1 = (page - 1) * rowsPerPage;
            const end1 = start1 + rowsPerPage;
            const paginatedData1 = new_task_list.slice(start1, end1);
    
            for (var i = 0; i < paginatedData1.length; i++) {
                var row = document.createElement("tr");
    
                for (var key in paginatedData1[i]) {
                    if (key !== 'id') {
                        var cell = document.createElement("td");
                        cell.classList.add("center-text");
    
                        // if (key === 'priority_display') {
                        //     // Priority styling
                        //     var priorityDiv = document.createElement("div");
                        //     priorityDiv.style.color = "black";
                        //     priorityDiv.style.padding = "3px 9px";
                        //     priorityDiv.style.borderRadius = "5px";
                        //     priorityDiv.style.textAlign = "center"; // Center text
    
                        //     // Apply background color based on priority
                        //     var priorityValue = paginatedData1[i][key].toLowerCase(); // Convert to lowercase
                        //     switch (priorityValue) {
                        //         case 'low':
                        //             priorityDiv.style.backgroundColor = "lightgray"; // Low priority
                        //             break;
                        //         case 'high':
                        //             priorityDiv.style.backgroundColor = "lightpink"; // High priority
                        //             break;
                        //         // default:
                        //         //     priorityDiv.style.backgroundColor = "lightgray"; // Default color for unknown priority
                        //     }
    
                        //     priorityDiv.textContent = paginatedData1[i][key];
                        //     cell.appendChild(priorityDiv);
                        // } 
                        // else if (Array.isArray(paginatedData1[i][key]) && paginatedData1[i][key].length === 2) {
                        //     cell.textContent = paginatedData1[i][key][1];
                        // } 
                        if (key === 'priority_display') {
                            // Priority styling
                            var priorityDiv = document.createElement("div");
                            priorityDiv.style.padding = "3px 9px";
                            priorityDiv.style.borderRadius = "5px";
                            priorityDiv.style.textAlign = "center"; // Center text
                        
                            // Create the Font Awesome flag icon element
                            var flagIcon = document.createElement("i");
                            flagIcon.classList.add("fa", "fa-flag-o"); // Add Font Awesome flag icon class
                        
                            // Apply background color and tooltip based on priority
                            var priorityValue = paginatedData1[i][key].toLowerCase(); // Convert to lowercase
                            switch (priorityValue) {
                                case 'low':
                                    flagIcon.style.color = "green"; // Green flag for low priority
                                    flagIcon.title = "Low Priority"; // Tooltip when hovering
                                    break;
                                case 'high':
                                    flagIcon.style.color = "red"; // Red flag for high priority
                                    flagIcon.title = "High Priority"; // Tooltip when hovering
                                    break;
                                
                            }
                        
                            // Append the flag icon to the div
                            priorityDiv.appendChild(flagIcon);
                            
                            // Append the div to the cell
                            cell.appendChild(priorityDiv);
                        } else if (Array.isArray(paginatedData1[i][key]) && paginatedData1[i][key].length === 2) {
                            cell.textContent = paginatedData1[i][key][1];
                        }
                        else if (key === 'date_deadline') {
                            var date_deadline = paginatedData1[i]['date_deadline'];
                            if (date_deadline) {
                                var today = new Date();
                                var taskDate = new Date(date_deadline);
                                var timeDiff = taskDate.getTime() - today.getTime();
                                var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
    
                                var dueDateDisplay = "";
                                var dueDateDiv = document.createElement("div");
                                dueDateDiv.style.padding = "3px 9px";
                                dueDateDiv.style.borderRadius = "5px";
                                dueDateDiv.style.textAlign = "center";  // Center the text
    
                                if (diffDays === 0) {
                                    dueDateDisplay = "Today";
                                    dueDateDiv.style.backgroundColor = "#ffea80"; // Yellow for today
                                    dueDateDiv.style.color = "black"; // Black text for today
                                } else if (diffDays > 0) {
                                    dueDateDisplay = diffDays + " days";
                                    dueDateDiv.style.backgroundColor = "#8aad84"; // Green for future dates
                                    dueDateDiv.style.color = "black"; // Black text for future
                                } else {
                                    dueDateDisplay = Math.abs(diffDays) + " days ago";
                                    dueDateDiv.style.backgroundColor = "#ff8a63"; // Red for past dates
                                    dueDateDiv.style.color = "black"; // White text for past
                                }
    
                                dueDateDiv.textContent = dueDateDisplay;
                                cell.appendChild(dueDateDiv);
                            } else {
                                cell.textContent = '-';
                            }
                        } else {
                            cell.textContent = paginatedData1[i][key] || '-';
                        }
    
                        row.appendChild(cell);
                    }
                }
    
                var buttonCell = document.createElement("td");
                var button = document.createElement("button");
                button.textContent = "View";
                button.setAttribute("data-id", paginatedData1[i].id);
                button.addEventListener("click", function () {
                    var id = this.getAttribute("data-id");
                    task_tree_button_function(id);
                });
                button.style.backgroundColor = "Pink";
                button.style.color = "black";
                button.style.padding = "3px 9px";
                buttonCell.appendChild(button);
                row.appendChild(buttonCell);
                tbody.appendChild(row);
            }
    
            function task_tree_button_function(id) {
                var options = {};
                self.action.doAction({
                    name: _t("Total Task"),
                    type: 'ir.actions.act_window',
                    res_model: 'project.task',
                    domain: [["id", "=", id]],
                    view_mode: 'list,form',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current'
                }, options);
            }
        });
    }
    

    prevsPage(e) {

        if (this.state.currentrecPage > 1) {
            this.state.currentrecPage--;
            this.render_task_table_data(this.state.rowsPerPage, this.state.currentrecPage);
            document.getElementById("nextt_button").disabled = false;
        }
        if (this.state.currentrecPage == 1)
        {
            document.getElementById("prevs_button").disabled = true;
        } else {
            document.getElementById("prevs_button").disabled = false;
        }
    }
    nexttPage() {
        if ((this.state.currentrecPage * this.state.rowsPerPage) < this.state.totalrecrows) {
            this.state.currentrecPage++;
            this.render_task_table_data(this.state.rowsPerPage, this.state.currentrecPage);
            document.getElementById("prevs_button").disabled = false;
        }
        if (Math.ceil(this.state.totalrecrows / this.state.rowsPerPage) == this.state.currentrecPage)
        {
            document.getElementById("nextt_button").disabled = true;
        } else {
            document.getElementById("nextt_button").disabled = false;
        }
    }

    // =====activity table 22======
    async render_activity_table_data(rowsPerPage,page) {
        var pruser_selection = document.querySelector("#pruser_selection").value;
        var prpartner_selection = document.querySelector("#prpartner_selection").value;
        var prproject_selection = document.querySelector("#prproject_selection").value;
        var duration_selection = document.querySelector("#duration_selection").value;
        var view_id = this.state.view_id;
        var self = this;
        await jsonrpc("/project/table/data",
        {
        'data':
            {
                'user_id': pruser_selection,
                'partner_id': prpartner_selection, 
                'project_id': prproject_selection,
                'duration':duration_selection, 
                'view_id': view_id
                
            }
        }).then(function (data) 
        {
               
        var activity_task_list = data['activity_task_list'];
        self.state.totaldelrows = activity_task_list.length;
        var tbody = document.querySelector("#my_table_activity_task_list tbody");
        tbody.innerHTML = '';
        
        const start2 = (page - 1) * rowsPerPage;
        const end2 = start2 + rowsPerPage;
        const paginatedData2 = activity_task_list.slice(start2, end2)
        
        for (var i = 0; i < paginatedData2.length; i++) {
            // Create a new row
            var row = document.createElement("tr");
            // Create cells for each property in the object
            for (var key in paginatedData2[i]) {
                if (key !== 'id') {
                    var cell = document.createElement("td");
                    cell.classList.add("center-text");
                    if (paginatedData2[i][key].length == 2) {
                        cell.textContent = paginatedData2[i][key][1];
                        row.appendChild(cell);
                    }
                    
                    else {
                        if (paginatedData2[i][key] == false) {
                            cell.textContent = '-';
                            row.appendChild(cell);
                        } else {
                            cell.textContent = paginatedData2[i][key];
                            row.appendChild(cell);
                        }
                    }
                }
            }
        var buttonCell = document.createElement("td");
        var button = document.createElement("button");
        button.textContent = "View";
        button.setAttribute("data-id", paginatedData2[i].id);
        button.addEventListener("click", function() {
        var id = this.getAttribute("data-id");
            // Call your function with the ID
            activity_tree_button_function(id);
        });
        button.style.backgroundColor = "Pink";
        button.style.color = "black";
        button.style.padding = "3px 9px";
        buttonCell.appendChild(button);
        row.appendChild(buttonCell);
        tbody.appendChild(row);
        }
        
        function activity_tree_button_function(id) {
            var options = {
            };
            self.action.doAction({
                name: _t("Total Activity"),
                type: 'ir.actions.act_window',
                res_model: 'mail.activity',
                domain: [["id", "=", id]],
                view_mode: 'list,form',
                views: [
                    [false, 'list'],
                    [data.view_id, 'form']
                ],
                target: 'current'
            }, options)
        }
    })
    }

    prevsPages(e) {

        if (this.state.currentdelPage > 1) {
            this.state.currentdelPage--;
            this.render_activity_table_data(this.state.rowsPerPage, this.state.currentdelPage);
            document.getElementById("nextt_buttons").disabled = false;
        }
        if (this.state.currentdelPage == 1)
        {
            document.getElementById("prevs_buttons").disabled = true;
        } else {
            document.getElementById("prevs_buttons").disabled = false;
        }
    }
    nexttPages() {
        if ((this.state.currentdelPage * this.state.rowsPerPage) < this.state.totaldelrows) {
            this.state.currentdelPage++;
            this.render_activity_table_data(this.state.rowsPerPage, this.state.currentdelPage);
            document.getElementById("prevs_buttons").disabled = false;
        }
        if (Math.ceil(this.state.totaldelrows / this.state.rowsPerPage) == this.state.currentdelPage)
        {
            document.getElementById("nextt_buttons").disabled = true;
        } else {
            document.getElementById("nextt_buttons").disabled = false;
        }
    }

}
                        
ProjectDashboard.template = "projectdashboard"
registry.category("actions").add("open_project_dashboard", ProjectDashboard)
