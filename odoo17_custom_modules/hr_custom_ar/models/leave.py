from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrLeaveCustom(models.Model):
    _name = 'hr.leave.custom'
    _description = 'طلب إجازة'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='الرقم',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.leave.custom'),
        readonly=True
    )
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)

    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(
        related='employee_id.department_id',
        string='القسم',
        store=True,
        readonly=True
    )

    # حقول التقويم: بداية/نهاية الإجازة
    date_from = fields.Datetime(string='تاريخ بداية الإجازة', required=True)
    date_to   = fields.Datetime(string='تاريخ نهاية الإجازة', required=True)

    reason = fields.Char(string='السبب')

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('approved', 'معتمد'),
        ('returned', 'تمت المباشرة')
    ], default='draft', string='الحالة')

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_return(self):
        self.write({'state': 'returned'})

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError('تاريخ نهاية الإجازة يجب أن يكون بعد تاريخ بدايتها.')
