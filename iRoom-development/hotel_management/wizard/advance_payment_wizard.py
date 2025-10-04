from odoo import fields, models, api
import time
import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class advance_payment_wizard(models.TransientModel):
    _name = 'advance.payment.wizard'
    _description = 'Advance Payment Detail Wizard'

    amt = fields.Float('Amount')

    deposit_recv_acc = fields.Many2one(
        'account.account', string="Deposit Account", required=True)
    journal_id = fields.Many2one(
        'account.journal', "Journal", required=True, domain="[('type','=',('cash','bank'))]")
    reservation_id = fields.Many2one(
        'hotel.reservation', 'Reservation Ref', default=lambda self: self._get_default_rec())
    payment_date = fields.Date(
        'Payment Date', required=True, default=fields.Date.context_today)

    @api.model
    def default_get(self, fields):
        res = super(advance_payment_wizard, self).default_get(fields)
        if self._context:
            active_model = self._context.get('active_model')
            if active_model == 'hotel.room':
                active_model = 'hotel.reservation'
            active_model_id = self.env[active_model].browse(self._context.get('active_id'))
            if active_model_id:
                if active_model_id.partner_id.property_account_receivable_id:
                    res['deposit_recv_acc'] = active_model_id.partner_id.property_account_receivable_id.id
        return res

    def _get_default_rec(self):
        res = {}
        if self._context is None:
            self._context = {}
        if 'reservation_id' in self._context:
            res = self._context['reservation_id']
        return res

    # @api.multi

    def payment_process(self):
        sum = 0
        remainder = 0
        #   "context-------------------------------------------", self.browse(self._ids))
        if self._context.get('active_model') == 'hotel.folio' :#or self._context.get('active_model') == 'hotel.reservation':
            for obj in self:
                folio_obj = self.env['hotel.folio'].search([('reservation_id', '=', obj.reservation_id.id)])
                if folio_obj:
                    folio_id = folio_obj[0]
                else:
                    folio_id = False
                if not obj.deposit_recv_acc:
                    raise UserError("Account is not set for Deposit account.")
                if not obj.journal_id.default_account_id:
                    raise UserError("Account is not set for selected journal.")
                if obj.amt > folio_id.remaining_amt:
                    raise UserError("Amount is more than folio remaining amount")
                name = ''
                seq_obj = self.env['ir.sequence']
                if obj.journal_id.secure_sequence_id:
                    name = seq_obj.get_id(obj.journal_id.secure_sequence_id.id)
                
                payment_id = self.env['account.payment'].create({
                    'journal_id': obj.journal_id.id,
                    'partner_id': obj.reservation_id.partner_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'amount': obj.amt,
                })
                payment_id.move_id.ref = obj.reservation_id.name
                payment_id.action_post()
                if folio_obj and folio_id.id:
                    folio_id.write({'payment_move_ids': [(4, payment_id.id)]  # 4 indicates to add a record
                    })
                    self._cr.execute('insert into sale_account_move_rel(sale_id, move_id) values (%s,%s)', (
                        folio_id.id, payment_id.move_id.id))
                    result = folio_id
                    sum = result.total_advance + obj.amt
                    remainder = folio_id.amount_total - sum
                    self.env['hotel.folio'].write({'total_advance': sum})
                    sale = self.env['sale.order'].search(
                        [('id', '=', folio_id.order_id.id)])
                    if sale:
                        rr = self.env['sale.order'].write(
                            {'remaining_amt': remainder})
                    sum = 0
                    remainder = 0
        else:
            for obj in self:
                if not obj.deposit_recv_acc:
                    raise UserError("Account is not set for Deposit account.")
                if not obj.journal_id.default_account_id:
                    raise UserError("Account is not set for selected journal.")
                if obj.amt > obj.reservation_id.remaining_amt:
                    raise UserError("Amount is more than reservation remaining amount")
                if obj.reservation_id.remaining_amt == 0:
                    break
                vals = {
                    'journal_id': obj.journal_id.id,
                    'partner_id': obj.reservation_id.partner_id.id,
                    # 'destination_account_id': obj.reservation_id.company_id.partner_id.property_account_receivable_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'amount': obj.amt,
                    'company_id':obj.reservation_id.company_id.id,
                    
                }

                payment_id = self.env['account.payment'].sudo().create(vals)
                payment_id.move_id.ref = obj.reservation_id.name
                # Relate Tx with payment
                tx_id = self.env['payment.transaction'].search([('reservation_ids', 'in', obj.reservation_id.ids), ('payment_id', '=', False)])
                if tx_id:
                    tx_id.write({'payment_id': payment_id.id})
                payment_id.sudo().action_post()
                obj.reservation_id.write({'payment_move_ids': [(4, payment_id.id)]  # 4 indicates to add a record
                })
                self._cr.execute(
                    'insert into reservation_account_move_rel(reservation_id,move_id) values (%s,%s)', (obj.reservation_id.id, payment_id.move_id.id))
                result = obj.reservation_id
                sum = result.total_advance + obj.amt
                remainder = result.total_cost1 - sum
                result.total_advance = sum
                sum = 0
                remainder = 0
                if obj.reservation_id.state == 'draft':
                    obj.reservation_id.confirmed_reservation()
        return {'type': 'ir.actions.act_window_close'}
