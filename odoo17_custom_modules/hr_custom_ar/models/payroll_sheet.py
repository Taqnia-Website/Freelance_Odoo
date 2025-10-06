from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrPayrollSheet(models.Model):
    _name = 'hr.payroll.sheet'
    _description = 'كشف رواتب (مخصص)'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='الرقم',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.payroll.sheet'),
        readonly=True
    )
    date = fields.Date(string='التاريخ', default=fields.Date.context_today, required=True)
    line_ids = fields.One2many('hr.payroll.sheet.line', 'sheet_id', string='الأسطر')
    state = fields.Selection(
        [('draft', 'مسودة'), ('done', 'معتمد'), ('posted', 'مسجل محاسبياً')],
        default='draft',
        string='الحالة'
    )

    # حقول محاسبية
    journal_id = fields.Many2one('account.journal', string='دفتر اليومية')
    move_id = fields.Many2one('account.move', string='القيد المحاسبي', readonly=True, copy=False)

    # حقول إجمالية
    total_basic = fields.Float(string='إجمالي الرواتب الأساسية', compute='_compute_totals', store=True)
    total_loans = fields.Float(string='إجمالي السلف', compute='_compute_totals', store=True)
    total_deductions = fields.Float(string='إجمالي الخصومات', compute='_compute_totals', store=True)
    total_overtime = fields.Float(string='إجمالي الإضافي', compute='_compute_totals', store=True)
    total_net = fields.Float(string='إجمالي الصافي', compute='_compute_totals', store=True)

    @api.depends('line_ids.basic_salary', 'line_ids.loan_total', 'line_ids.deduction_total',
                 'line_ids.overtime_total', 'line_ids.net_salary')
    def _compute_totals(self):
        for sheet in self:
            sheet.total_basic = sum(sheet.line_ids.mapped('basic_salary'))
            sheet.total_loans = sum(sheet.line_ids.mapped('loan_total'))
            sheet.total_deductions = sum(sheet.line_ids.mapped('deduction_total'))
            sheet.total_overtime = sum(sheet.line_ids.mapped('overtime_total'))
            sheet.total_net = sum(sheet.line_ids.mapped('net_salary'))

    def action_compute(self):
        for sheet in self:
            sheet.line_ids.unlink()

            date_from = sheet.date.replace(day=1)
            next_month = date_from + relativedelta(months=1)
            date_to = next_month - relativedelta(days=1)

            employees = self.env['hr.employee'].search([])

            for emp in employees:
                loans = sum(self.env['hr.loan'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to)
                ]).mapped('amount'))

                deductions = sum(self.env['hr.deduction'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to)
                ]).mapped('amount'))

                overtimes = sum(self.env['hr.overtime'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to)
                ]).mapped('total'))

                basic_salary = 0.0
                if emp.contract_id and emp.contract_id.state == 'open':
                    basic_salary = emp.contract_id.wage

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

    def action_post_accounting(self):
        """إنشاء قيد محاسبي لكشف الرواتب"""
        for sheet in self:
            if not sheet.journal_id:
                raise UserError('يرجى تحديد دفتر اليومية أولاً.')

            if not sheet.line_ids:
                raise UserError('لا توجد أسطر في كشف الرواتب.')

            # البحث عن حسابات محاسبية (يمكن تخصيصها حسب دليل الحسابات)
            # هنا نستخدم حسابات افتراضية من دفتر اليومية
            if not sheet.journal_id.default_account_id:
                raise UserError('يرجى تحديد الحساب الافتراضي في دفتر اليومية.')

            # إنشاء القيد المحاسبي
            move_lines = []

            # مدين: مصروف الرواتب (إجمالي الصافي)
            move_lines.append((0, 0, {
                'name': f'رواتب {sheet.name}',
                'account_id': sheet.journal_id.default_account_id.id,
                'debit': sheet.total_net,
                'credit': 0.0,
            }))

            # دائن: البنك/الصندوق (إجمالي الصافي)
            move_lines.append((0, 0, {
                'name': f'صرف رواتب {sheet.name}',
                'account_id': sheet.journal_id.default_account_id.id,
                'debit': 0.0,
                'credit': sheet.total_net,
            }))

            # إنشاء القيد
            move = self.env['account.move'].create({
                'journal_id': sheet.journal_id.id,
                'date': sheet.date,
                'ref': sheet.name,
                'line_ids': move_lines,
            })

            move.action_post()
            sheet.move_id = move.id
            sheet.state = 'posted'

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