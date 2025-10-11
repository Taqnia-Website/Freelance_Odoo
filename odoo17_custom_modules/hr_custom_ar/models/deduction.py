from odoo import models, fields

class HrDeduction(models.Model):
    _name = 'hr.deduction'
    _description = 'خصم موظف'
    _order = 'date desc, id desc'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.deduction'), readonly=True)
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    amount = fields.Float(string='مبلغ الخصم', required=True)
    reason = fields.Char(string='سبب الخصم')
    state = fields.Selection([('draft','مسودة'),('approved','معتمد')], default='draft', string='الحالة')

    def action_approve(self):
        self.write({'state':'approved'})