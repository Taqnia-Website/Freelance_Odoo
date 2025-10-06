from odoo import models, fields,api

class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _description = 'إضافي موظف'
    _order = 'date desc, id desc'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.overtime'), readonly=True)
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    amount = fields.Float(string='مبلغ الإضافي', required=True)
    hours = fields.Float(string='عدد ساعات الإضافي', required=True)
    total = fields.Float(string='الإجمالي', compute='_compute_total', store=True)
    state = fields.Selection([('draft','مسودة'),('approved','معتمد')], default='draft', string='الحالة')

    @api.depends('amount','hours')
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.amount or 0.0) * (rec.hours or 0.0)

    def action_approve(self):
        self.write({'state':'approved'})