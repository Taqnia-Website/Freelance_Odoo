from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrPayrollSheet(models.Model):
    _name = 'hr.payroll.sheet'
    _description = 'كشف رواتب (مخصص)'
    _order = 'date desc, id desc'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.payroll.sheet'),
                       readonly=True)
    date = fields.Date(string='التاريخ', default=fields.Date.context_today, required=True)
    line_ids = fields.One2many('hr.payroll.sheet.line', 'sheet_id', string='الأسطر')
    state = fields.Selection([('draft', 'مسودة'), ('done', 'معتمد')], default='draft', string='الحالة')

    def action_compute(self):
        for sheet in self:
            # حذف الأسطر القديمة
            sheet.line_ids.unlink()

            # حساب بداية ونهاية الشهر
            date_from = sheet.date.replace(day=1)  # أول يوم في الشهر

            # آخر يوم في الشهر
            next_month = date_from + relativedelta(months=1)
            date_to = next_month - relativedelta(days=1)

            # جلب جميع الموظفين
            employees = self.env['hr.employee'].search([])

            for emp in employees:
                # حساب السلف المعتمدة في الشهر
                loans = sum(self.env['hr.loan'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to)
                ]).mapped('amount'))

                # حساب الخصومات المعتمدة في الشهر
                deductions = sum(self.env['hr.deduction'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to)
                ]).mapped('amount'))

                # حساب الإضافي المعتمد في الشهر
                overtimes = sum(self.env['hr.overtime'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to)
                ]).mapped('total'))

                # جلب الراتب الأساسي من العقد
                basic_salary = 0.0
                if emp.contract_id and emp.contract_id.state == 'open':
                    basic_salary = emp.contract_id.wage

                # إنشاء سطر جديد
                self.env['hr.payroll.sheet.line'].create({
                    'sheet_id': sheet.id,
                    'employee_id': emp.id,
                    'basic_salary': basic_salary,
                    'loan_total': loans,
                    'deduction_total': deductions,
                    'overtime_total': overtimes,
                })

    def action_done(self):
        self.write({'state': 'done'})

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref('hr_custom_ar.action_hr_payroll_sheet_pdf').report_action(self)

    def action_export_xlsx(self):
        self.ensure_one()
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

    @api.depends('basic_salary', 'loan_total', 'deduction_total', 'overtime_total')
    def _compute_net(self):
        for rec in self:
            rec.net_salary = (rec.basic_salary or 0.0) - (rec.loan_total or 0.0) - (rec.deduction_total or 0.0) + (
                        rec.overtime_total or 0.0)