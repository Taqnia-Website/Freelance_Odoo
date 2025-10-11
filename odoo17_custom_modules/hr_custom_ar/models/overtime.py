# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _description = 'إضافي موظف'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='الرقم',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.overtime'),
        readonly=True
    )
    date = fields.Date(
        string='تاريخ اليوم',
        default=fields.Date.context_today,
        required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='اسم الموظف',
        required=True
    )
    department_id = fields.Many2one(
        related='employee_id.department_id',
        string='القسم',
        store=True,
        readonly=True
    )
    hours = fields.Float(
        string='عدد ساعات الإضافي',
        required=True
    )
    hourly_rate = fields.Float(
        string='سعر الساعة',
        compute='_compute_hourly_rate',
        store=True,
        readonly=True
    )
    total = fields.Float(
        string='الإجمالي',
        compute='_compute_total',
        store=True
    )
    state = fields.Selection(
        [('draft', 'مسودة'), ('approved', 'معتمد')],
        default='draft',
        string='الحالة'
    )

    @api.depends('employee_id')
    def _compute_hourly_rate(self):
        """حساب سعر الساعة = (الراتب الأساسي / 30 / 8)"""
        for rec in self:
            if rec.employee_id and rec.employee_id.contract_id:
                basic_salary = rec.employee_id.contract_id.wage
                # سعر الساعة = الراتب الأساسي / 30 يوم / 8 ساعات
                rec.hourly_rate = basic_salary / 30.0 / 8.0
            else:
                rec.hourly_rate = 0.0

    @api.depends('hours', 'hourly_rate')
    def _compute_total(self):
        """حساب الإجمالي = (عدد الساعات × 1.5 × سعر الساعة)"""
        for rec in self:
            # الإجمالي = ساعات × 1.5 × سعر الساعة
            rec.total = (rec.hours or 0.0) * 1.5 * (rec.hourly_rate or 0.0)

    def action_approve(self):
        for rec in self:
            if not rec.employee_id.contract_id:
                raise UserError(
                    f'الموظف "{rec.employee_id.name}" ليس لديه عقد نشط!\n'
                    f'يرجى إنشاء عقد للموظف أولاً من: الموارد البشرية → العقود'
                )
            if rec.hourly_rate <= 0:
                raise UserError(
                    f'سعر الساعة للموظف "{rec.employee_id.name}" يساوي صفر!\n'
                    f'يرجى التأكد من وجود راتب أساسي في العقد.'
                )
        self.write({'state': 'approved'})
# from odoo import models, fields,api
#
# class HrOvertime(models.Model):
#     _name = 'hr.overtime'
#     _description = 'إضافي موظف'
#     _order = 'date desc, id desc'
#
#     name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.overtime'), readonly=True)
#     date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
#     employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
#     department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
#     amount = fields.Float(string='مبلغ الإضافي', required=True)
#     hours = fields.Float(string='عدد ساعات الإضافي', required=True)
#     total = fields.Float(string='الإجمالي', compute='_compute_total', store=True)
#     state = fields.Selection([('draft','مسودة'),('approved','معتمد')], default='draft', string='الحالة')
#
#     @api.depends('amount','hours')
#     def _compute_total(self):
#         for rec in self:
#             rec.total = (rec.amount or 0.0) * (rec.hours or 0.0)
#
#     def action_approve(self):
#         self.write({'state':'approved'})