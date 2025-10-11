# hr_custom_ar/models/loan.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class HrLoan(models.Model):
    _name = 'hr.loan'
    _description = 'سلفة موظف'
    _order = 'date desc, id desc'

    # بيانات عامة
    name = fields.Char(string='الرقم', default=lambda self: self.env['ir.sequence'].next_by_code('hr.loan'), readonly=True)
    date = fields.Date(string='تاريخ اليوم', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='اسم الموظف', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='القسم', store=True, readonly=True)
    amount = fields.Float(string='مبلغ السلفة', required=True)
    months = fields.Integer(string='عدد شهور الاستقطاع', default=1)
    reason = fields.Char(string='سبب السلفة')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('approved', 'معتمد'),
        ('paid', 'مسجل محاسبياً'),
    ], default='draft', string='الحالة')

    # محاسبة
    journal_id = fields.Many2one('account.journal', string='دفتر اليومية', domain="[('company_id','=',company_id)]")
    move_id = fields.Many2one('account.move', string='القيد', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, readonly=True)

    # حسابات اختيارية على مستوى السلفة (لو مش عايزة تعتمدي على الافتراضي بتاع الدفتر)
    debit_account_id = fields.Many2one(
        'account.account', string='حساب مدين (سلف/ذمم موظفين)',
        domain="[('company_id','=',company_id), ('deprecated','=',False)]")
    credit_account_id = fields.Many2one(
        'account.account', string='حساب دائن (صندوق/بنك/التزامات)',
        domain="[('company_id','=',company_id), ('deprecated','=',False)]")

    def action_approve(self):
        self.write({'state': 'approved'})

    # يجيب Partner للموظف لو متاح بدون ما يفرض وجوده
    def _get_partner_for_move(self):
        self.ensure_one()
        partner = False
        for field in ('work_contact_id', 'address_home_id', 'address_id'):
            if field in self.employee_id._fields:
                partner = self.employee_id[field]
                if partner:
                    break
        return partner

    # يحدد حسابات القيد (من حقول السلفة أو من الدفتر)
    def _get_accounts(self):
        self.ensure_one()
        j = self.journal_id
        debit_acc = self.debit_account_id \
                    or (j and getattr(j, 'default_account_id', False)) \
                    or (j and getattr(j, 'default_debit_account_id', False))
        credit_acc = self.credit_account_id \
                     or (j and getattr(j, 'default_account_id', False)) \
                     or (j and getattr(j, 'default_credit_account_id', False))
        if not debit_acc or not credit_acc:
            raise UserError('يجب تحديد حسابات المدين/الدائن (إما من حقول السلفة أو كافتراضي في دفتر اليومية).')
        return debit_acc, credit_acc

    def action_post_account(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError('قيمة السلفة يجب أن تكون أكبر من صفر.')
            if not rec.journal_id:
                raise UserError('يرجى تحديد دفتر اليومية.')

            debit_acc, credit_acc = rec._get_accounts()
            partner = rec._get_partner_for_move()
            line_name = f"سلفة: {rec.employee_id.name or ''}"

            vals = {
                'journal_id': rec.journal_id.id,
                'date': rec.date,
                'ref': rec.name,
                'line_ids': [
                    (0, 0, {
                        'name': line_name,
                        'account_id': debit_acc.id,
                        'debit': rec.amount,
                        'credit': 0.0,
                        'partner_id': partner.id if partner else False,
                    }),
                    (0, 0, {
                        'name': line_name,
                        'account_id': credit_acc.id,
                        'debit': 0.0,
                        'credit': rec.amount,
                        'partner_id': partner.id if partner else False,
                    }),
                ],
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            rec.move_id = move.id
            rec.state = 'paid'
