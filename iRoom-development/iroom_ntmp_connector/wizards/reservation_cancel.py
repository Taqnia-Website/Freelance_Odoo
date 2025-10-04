import requests
import json
from requests.auth import HTTPBasicAuth
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ReservationCancel(models.TransientModel):
    _name = 'reservation.cancel'
    _description = 'Folio Cancel'

    reservation_id = fields.Many2one('hotel.reservation')
    folio_id = fields.Many2one('hotel.folio')
    reason_id = fields.Many2one('ntmp.cancel.reason', required=True)
    cancel_with_charge = fields.Selection(selection=[
        ('1', 'Yes'), ('0', 'No')
    ], required=True)
    chargeable_days = fields.Integer(default=0)

    def button_cancel_reservation(self):
        if self.reservation_id:
            reservation_id = self.reservation_id
        else:
            reservation_id = self.folio_id.reservation_id
        lines = reservation_id.reservation_line
        for line in lines:
            # todo check paid amount and chargeable_days are matching!
            if self.cancel_with_charge == '1' and self.chargeable_days <= 0:
                raise ValidationError("chargeable days must be more than 0!")
            # url = "https://api.ntmp.gov.sa/gateway/CancelBooking/1.0/cancelBooking"
            url = "https://dev-api.ntmp.gov.sa/gateway/CancelBooking/1.0/cancelBooking"
            headers = line.line_id.prepare_ntmp_headers()
            data = self.prepare_data(line)
            response = requests.post(url=url, headers=headers, json=data, auth=HTTPBasicAuth(line.company_id.ntmp_username, line.company_id.ntmp_password))
            txt = json.loads(response.text)
            if txt.get('errorCode', False):
                error_code = txt['errorCode'][0]
                message = self.get_response_msg(error_code)
                if self.reservation_id:
                    self.reservation_id.message_post(body=f"Transaction ID: {line.ntmp_transaction_id}, {response.text}, {message}")
                else:
                    self.folio_id.message_post(body=f"Transaction ID: {line.ntmp_transaction_id}, {response.text}, {message}")
        if self.reservation_id:
            self.reservation_id.with_context(ignore_ntmp=True).cancel_reservation()
        else:
            self.folio_id.with_context(ignore_ntmp=True).action_cancel()
        days = reservation_id.get_reservation_days()
        for day in days:
            reservation_id.ntmp_update_occupancy(day)

    def prepare_data(self, line):
        if self.cancel_with_charge == '1' and line.number_of_days > 0:
            daily_room_rate = str(line.sub_total1 / line.number_of_days)
        else:
            daily_room_rate = "0"
        return {
            "transactionId": line.ntmp_transaction_id,
            "cancelReason": self.reason_id.code,
            "cancelWithCharges": self.cancel_with_charge,
            "chargeableDays": str(self.chargeable_days) if self.chargeable_days and self.cancel_with_charge == '1' else "0",
            "roomRentType": line.rent_type_id.code if line.rent_type_id else "1",
            "dailyRoomRate": daily_room_rate,
            "totalRoomRate": str(line.sub_total1) if line.sub_total1 and self.cancel_with_charge == '1' else "0",
            "vat": "0",  # todo to be handled
            "municipalityTax": "0",  # todo to be handled
            "discount": "0",  # todo to be handled
            "grandTotal": str(line.sub_total1) if line.sub_total1 and self.cancel_with_charge == '1' else "0",
            "userId": line.company_id.ntmp_username or "",
            "paymentType": "4",
            "cuFlag": "2",
            "esbRefNo": "",
            "channel": line.company_id.ntmp_channel
        }

    def get_response_msg(self, code):
        msg = False
        if code:
            response = self.env['ntmp.response.code'].search([
                ('api_name', '=', 'cancelBooking'), ('error_code', '=', code)
            ], limit=1)
            if response:
                if response.category == 'success':
                    msg = 'Synced Successfully with NTMP'
                else:
                    msg = response.error_description
        return msg
