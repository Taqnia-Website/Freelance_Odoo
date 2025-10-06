from odoo import models, fields

class HrResignation(models.Model):
    _name = 'hr.resignation'
    _description = 'استقالة موظف'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.resignation'), readonly=True)
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    reason = fields.Char(string='سبب الاستقالة')
    state = fields.Selection([('draft','مسودة'),('accepted','مقبولة')], default='draft', string='الحالة')

    def action_accept(self):
        self.write({'state':'accepted'})