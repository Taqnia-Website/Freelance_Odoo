# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrPayrollSheet(models.Model):
    _name = 'hr.payroll.sheet'
    _description = 'كشف رواتب'
    _order = 'date desc, id desc'

    # بيانات عامة
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

    # إعدادات محاسبية
    journal_id = fields.Many2one('account.journal', string='دفتر اليومية')
    debit_account_id = fields.Many2one('account.account', string='حساب مدين (اختياري)')
    credit_account_id = fields.Many2one('account.account', string='حساب دائن (اختياري)')
    move_id = fields.Many2one('account.move', string='القيد المحاسبي', readonly=True, copy=False)

    # إجماليات
    total_basic = fields.Float(string='إجمالي الرواتب الأساسية', compute='_compute_totals', store=True)
    total_loans = fields.Float(string='إجمالي السلف', compute='_compute_totals', store=True)
    total_deductions = fields.Float(string='إجمالي الخصومات', compute='_compute_totals', store=True)
    total_overtime = fields.Float(string='إجمالي الإضافي', compute='_compute_totals', store=True)
    total_net = fields.Float(string='إجمالي الصافي', compute='_compute_totals', store=True)

    # -------------------- Helpers --------------------
    def _month_bounds(self, d):
        """يرجع أول وآخر يوم في شهر تاريخ الشيت"""
        d = fields.Date.to_date(d)
        first = d.replace(day=1)
        last = first + relativedelta(months=1, days=-1)
        return first, last

    @api.depends('line_ids.basic_salary', 'line_ids.loan_total',
                 'line_ids.deduction_total', 'line_ids.overtime_total',
                 'line_ids.net_salary')
    def _compute_totals(self):
        for sheet in self:
            sheet.total_basic = sum(sheet.line_ids.mapped('basic_salary'))
            sheet.total_loans = sum(sheet.line_ids.mapped('loan_total'))
            sheet.total_deductions = sum(sheet.line_ids.mapped('deduction_total'))
            sheet.total_overtime = sum(sheet.line_ids.mapped('overtime_total'))
            sheet.total_net = sum(sheet.line_ids.mapped('net_salary'))

    # -------------------- Compute Sheet --------------------
    def action_compute(self):
        """يحسب السطور للشهر المحدد في الشيت"""
        Overtime = self.env['hr.overtime']
        overtime_amount_field = 'amount' if 'amount' in Overtime._fields else 'total'

        for sheet in self:
            # نظّف السطور القديمة
            sheet.line_ids.unlink()

            date_from, date_to = self._month_bounds(sheet.date)

            employees = self.env['hr.employee'].search([])
            vals_list = []

            for emp in employees:
                # الراتب الأساسي
                basic_salary = 0.0
                if getattr(emp, 'contract_id', False) and emp.contract_id and emp.contract_id.state == 'open':
                    basic_salary = float(getattr(emp.contract_id, 'wage', 0.0) or 0.0)

                # السلف (approved/paid) خلال الشهر - بالقسط الشهري
                loans = self.env['hr.loan'].search([
                    ('employee_id', '=', emp.id),
                    ('state', 'in', ('approved', 'paid')),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                ])
                loan_total = sum(round((l.amount or 0.0) / float(l.months or 1), 2) for l in loans)

                # الخصومات خلال الشهر
                deductions = self.env['hr.deduction'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                ])
                deduction_total = sum(d.amount or 0.0 for d in deductions)

                # الإضافي خلال الشهر
                overtimes = self.env['hr.overtime'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'approved'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                ])
                overtime_total = sum(getattr(o, overtime_amount_field, 0.0) or 0.0 for o in overtimes)

                vals_list.append((0, 0, {
                    'employee_id': emp.id,
                    'basic_salary': basic_salary,
                    'loan_total': loan_total,
                    'deduction_total': deduction_total,
                    'overtime_total': overtime_total,
                }))

            if vals_list:
                sheet.write({'line_ids': vals_list})

        return True

    # -------------------- Workflow --------------------
    def action_done(self):
        self.write({'state': 'done'})
        return True

    # -------------------- Accounting --------------------
    def action_post_accounting(self):
        """إنشاء قيد محاسبي لإجمالي صافي الرواتب"""
        for sheet in self:
            if not sheet.journal_id:
                raise UserError('يرجى تحديد دفتر اليومية أولاً.')
            if not sheet.line_ids:
                raise UserError('لا توجد أسطر في كشف الرواتب.')
            if sheet.total_net <= 0.0:
                raise UserError('إجمالي الصافي صفر. لا يمكن إنشاء قيد.')

            # اختيار حسابات مدين/دائن
            # يجب تحديد الحسابات صراحة على مستوى كشف الرواتب
            if not sheet.debit_account_id or not sheet.credit_account_id:
                raise UserError(
                    'يرجى تحديد حساب المدين (مصروف الرواتب) وحساب الدائن (البنك/الصندوق) '
                    'في قسم الإعدادات المحاسبية أسفل النموذج.'
                )

            debit_acc = sheet.debit_account_id
            credit_acc = sheet.credit_account_id

            if debit_acc.id == credit_acc.id:
                raise UserError('حساب المدين والدائن متطابقان. يرجى اختيار حسابين مختلفين.')

            move_vals = {
                'journal_id': sheet.journal_id.id,
                'date': sheet.date,
                'ref': sheet.name,
                'line_ids': [
                    # مدين: مصروف/أجور
                    (0, 0, {
                        'name': f'رواتب {sheet.name}',
                        'account_id': debit_acc.id,
                        'debit': sheet.total_net,
                        'credit': 0.0,
                    }),
                    # دائن: بنك/صندوق/دائن رواتب
                    (0, 0, {
                        'name': f'صرف رواتب {sheet.name}',
                        'account_id': credit_acc.id,
                        'debit': 0.0,
                        'credit': sheet.total_net,
                    }),
                ]
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            sheet.move_id = move.id
            sheet.state = 'posted'
        return True
    # -------------------- Reports/Export --------------------
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
            rec.net_salary = (rec.basic_salary or 0.0) \
                             - (rec.loan_total or 0.0) \
                             - (rec.deduction_total or 0.0) \
                             + (rec.overtime_total or 0.0)
