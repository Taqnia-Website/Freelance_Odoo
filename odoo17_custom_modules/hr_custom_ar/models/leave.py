from odoo import models, fields

class HrLeaveCustom(models.Model):
    _name = 'hr.leave.custom'
    _description = 'طلب إجازة'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.leave.custom'), readonly=True)
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    date_from = fields.Date(string='تاريخ بداية الإجازة', required=True)
    date_to = fields.Date(string='تاريخ نهاية الإجازة', required=True)
    reason = fields.Char(string='السبب')
    state = fields.Selection([('draft','مسودة'),('approved','معتمد'),('returned','تمت المباشرة')], default='draft', string='الحالة')

    def action_approve(self):
        self.write({'state':'approved'})