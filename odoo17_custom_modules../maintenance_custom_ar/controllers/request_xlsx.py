from odoo import http
from odoo.http import request
import io
import xlsxwriter

class MaintenanceXlsxController(http.Controller):

    @http.route('/maintenance_custom_ar/request/xlsx/<int:req_id>', type='http', auth='user')
    def export_request_xlsx(self, req_id, **kw):
        rec = request.env['maintenance.request.custom'].browse(req_id).sudo()
        if not rec.exists():
            return request.not_found()

        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet('Maintenance')

        headers = ['اسم القطعة', 'الكمية', 'السعر', 'الإجمالي']
        for col, h in enumerate(headers):
            ws.write(0, col, h)

        row = 1
        for line in rec.part_line_ids:
            ws.write(row, 0, line.product_id.display_name or '')
            ws.write(row, 1, line.quantity or 0.0)
            ws.write(row, 2, line.price_unit or 0.0)
            ws.write(row, 3, line.price_subtotal or 0.0)
            row += 1

        wb.close()
        output.seek(0)
        headers_http = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename=maintenance_{rec.id}.xlsx')
        ]
        return request.make_response(output.read(), headers=headers_http)
