from odoo import models, fields, api

class HrPayrollSheet(models.Model):
    _name = 'hr.payroll.sheet'
    _description = 'كشف رواتب (مخصص)'
    _order = 'date desc, id desc'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.payroll.sheet'), readonly=True)
    date = fields.Date(string='التاريخ', default=fields.Date.context_today, required=True)
    line_ids = fields.One2many('hr.payroll.sheet.line','sheet_id', string='الأسطر')
    state = fields.Selection([('draft','مسودة'),('done','معتمد')], default='draft', string='الحالة')

    def action_compute(self):
        for sheet in self:
            # recompute lines for all employees
            sheet.line_ids.unlink()
            employees = self.env['hr.employee'].search([])
            for emp in employees:
                # Collect totals from approved records
                loans = sum(self.env['hr.loan'].search_read([('employee_id','=',emp.id),('state','=','approved')], ['amount']), key=lambda x: x['amount']) if False else sum(l.amount for l in self.env['hr.loan'].search([('employee_id','=',emp.id),('state','=','approved')]))
                deds = sum(d.amount for d in self.env['hr.deduction'].search([('employee_id','=',emp.id),('state','=','approved')]))
                ots = sum(o.total for o in self.env['hr.overtime'].search([('employee_id','=',emp.id),('state','=','approved')]))
                self.env['hr.payroll.sheet.line'].create({
                    'sheet_id': sheet.id,
                    'employee_id': emp.id,
                    'basic_salary': emp.contract_id.wage if hasattr(emp, 'contract_id') and emp.contract_id else 0.0,
                    'loan_total': loans,
                    'deduction_total': deds,
                    'overtime_total': ots,
                })

    def action_done(self):
        self.write({'state':'done'})

    def action_print_pdf(self):
        self.ensure_one()
        # يستدعي الـ report اللي عرّفناه في hr_reports.xml
        return self.env.ref('hr_custom_ar.action_hr_payroll_sheet_pdf').report_action(self)

    def action_export_xlsx(self):
        self.ensure_one()
        # يفتح رابط الكونترولر لتوليد ملف Excel للروشتة الحالية
        return {
            'type': 'ir.actions.act_url',
            'url': f'/hr_custom_ar/payroll_sheet/xlsx/{self.id}',
            'target': 'self',
        }

class HrPayrollSheetLine(models.Model):
    _name = 'hr.payroll.sheet.line'
    _description = 'سطر كشف الرواتب'

    sheet_id = fields.Many2one('hr.payroll.sheet', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True)
    basic_salary = fields.Float(string='الراتب الأساسي')
    loan_total = fields.Float(string='السلف')
    deduction_total = fields.Float(string='الخصومات')
    overtime_total = fields.Float(string='الإضافي')
    net_salary = fields.Float(string='الصافي', compute='_compute_net', store=True)

    @api.depends('basic_salary','loan_total','deduction_total','overtime_total')
    def _compute_net(self):
        for rec in self:
            rec.net_salary = (rec.basic_salary or 0.0) - (rec.loan_total or 0.0) - (rec.deduction_total or 0.0) + (rec.overtime_total or 0.0)