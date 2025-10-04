from datetime import datetime
import json
import requests
from requests.auth import HTTPBasicAuth
from odoo import fields, models, api


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    def action_checkout(self):
        res = super(HotelFolio, self).action_checkout()
        for room_line in self.room_lines:
            booking_line = room_line.hotel_reservation_line_id
            if booking_line.line_id.apply_ntmp:
                booking_line.ntmp_connect(mode='check_out', new=False)
        if self.reservation_id.apply_ntmp and self.service_lines.filtered(lambda l: l.ntmp_service_id and l.ntmp_item_number):
            self.ntmp_expense_connect()
        return res

    def action_cancel(self):
        transactions = self.reservation_id.reservation_line.mapped('ntmp_transaction_id')
        ignore_ntmp = self.env.context.get('ignore_ntmp', False)
        if (self.reservation_id.apply_ntmp and transactions) and not ignore_ntmp:
            return {
                'type': 'ir.actions.act_window',
                'name': "Cancel Reservation",
                'res_model': 'reservation.cancel',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_folio_id': self.id,
                }
            }
        res = super(HotelFolio, self).action_cancel()
        return res

    # bookingExpense
    def ntmp_expense_connect(self):
        reservation_id = self.reservation_id
        url = "https://dev-api.ntmp.gov.sa/gateway/BookingExpense/1.0/bookingExpense"
        headers = reservation_id.prepare_ntmp_headers()
        data = self.prepare_expense_data()
        response = requests.post(url=url, headers=headers, json=data, auth=HTTPBasicAuth(self.company_id.ntmp_username, self.company_id.ntmp_password))
        txt = json.loads(response.text)
        if txt.get('errorCode', False):
            error_code = txt['errorCode'][0]
            msg = self.get_expense_response_msg(error_code)
            self.message_post(body=f"{response.text}, {msg}")

    def prepare_expense_data(self):
        transactions = self.reservation_id.reservation_line.mapped('ntmp_transaction_id')
        if transactions:
            return {
                "transactionId": transactions[0],
                "userId": self.company_id.ntmp_username or "",
                "channel": self.company_id.ntmp_channel or "",
                "expenseItems": self.prepare_expense_items()
            }
        else:
            return {}

    def prepare_expense_items(self):
        items = []
        for expense in self.service_lines.filtered(lambda l: l.ntmp_service_id and l.ntmp_item_number):
            total = expense.price_total
            # vat = self.line_ids.filtered(lambda l: l.related_line_id.id == expense.id and l.tax_type == 'vat')
            # if vat:
            #     total += vat.amount
            # municipality = self.line_ids.filtered(
            #     lambda l: l.related_line_id.id == expense.id and l.tax_type == 'municipality')
            # if municipality:
            #     total += municipality.amount

            items.append({
                "expenseDate": self.create_date.strftime('%Y%m%d'),
                "itemNumber": expense.ntmp_item_number,
                "expenseTypeId": expense.ntmp_service_id.code if expense.ntmp_service_id else "0",
                "unitPrice": str(round(expense.price_unit, 2)),
                "discount": str(expense.discount) if expense.discount else "0",
                # "vat": str(round(vat.amount, 2)) if vat else "0",
                # "municipalityTax": str(round(municipality.amount, 2)) if municipality else "0",
                "vat": "0",
                "municipalityTax": "0",
                "grandTotal": str(total),
                "paymentType": "1",
                "cuFlag": "1"
            })
        return items

    # todo refactor
    def get_expense_response_msg(self, code):
        msg = False
        if code:
            response = self.env['ntmp.response.code'].search([
                ('api_name', '=', 'bookingExpense'), ('error_code', '=', code)
            ], limit=1)
            if response:
                if response.category == 'success':
                    msg = 'Synced Successfully with NTMP'
                else:
                    msg = response.error_description
        return msg


class HotelServiceLine(models.Model):
    _inherit = 'hotel_service.line'

    ntmp_service_id = fields.Many2one('ntmp.expense.type', compute='compute_ntmp_service_id', store=True)
    ntmp_item_number = fields.Char()


    @api.depends('product_id')
    def compute_ntmp_service_id(self):
        for rec in self:
            rec.ntmp_service_id = False
            if rec.product_id:
                service = self.env['hotel.services'].search([('service_id', '=', rec.product_id.id)])
                if service:
                    rec.ntmp_service_id = service.ntmp_service_id.id

    @api.model
    def create(self, vals):
        vals['ntmp_item_number'] = str(datetime.today().timestamp())[:10]
        res = super(HotelServiceLine, self).create(vals)
        return res
