from odoo import models, fields, api
from odoo.exceptions import UserError

class HrLoan(models.Model):
    _name = 'hr.loan'
    _description = 'سلفة موظف'
    _order = 'date desc, id desc'

    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.loan'), readonly=True)
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    amount = fields.Float(string='مبلغ السلفة', required=True)
    months = fields.Integer(string='عدد شهور الاستقطاع', default=1)
    reason = fields.Char(string='سبب السلفة')
    state = fields.Selection([('draft','مسودة'),('approved','معتمد'),('paid','مسجل محاسبياً'),('cancel','ملغي')], default='draft', string='الحالة')
    journal_id = fields.Many2one('account.journal', string='دفتر اليومية')
    move_id = fields.Many2one('account.move', string='القيد', readonly=True, copy=False)

    def action_approve(self):
        self.write({'state':'approved'})

    def action_post_account(self):
        for rec in self:
            if not rec.journal_id:
                raise UserError('يرجى تحديد دفتر اليومية.')
            move = self.env['account.move'].create({
                'journal_id': rec.journal_id.id,
                'date': rec.date,
                'ref': rec.name,
                'line_ids': [
                    (0,0,{'name': 'سلفة: %s' % rec.employee_id.name, 'account_id': rec.journal_id.default_debit_account_id.id, 'debit': rec.amount, 'credit': 0.0}),
                    (0,0,{'name': 'سلفة: %s' % rec.employee_id.name, 'account_id': rec.journal_id.default_credit_account_id.id, 'debit': 0.0, 'credit': rec.amount}),
                ]
            })
            move.action_post()
            rec.move_id = move.id
            rec.state = 'paid'