from odoo import http
from odoo.http import request
import io
import xlsxwriter


class MaintExcelExport(http.Controller):

    @http.route(['/maintenance_custom_ar/request/xlsx/<int:req_id>'], type='http', auth='user')
    def maintenance_req_xlsx(self, req_id, **kw):
        req = request.env['maintenance.request.custom'].browse(req_id).sudo()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet('بيان طلب الصيانة')
        ws.write(0, 0, 'بيان طلب الصيانة')
        ws.write(1, 0, 'المسؤول')
        ws.write(1, 1, req.user_id.name or '')
        ws.write(2, 0, 'مدة التنفيذ')
        ws.write(2, 1, str(req.execution_duration) + ' يوم')
        ws.write(3, 0, 'تاريخ الطلب')
        ws.write(3, 1, str(req.date))
        ws.write(4, 0, 'اسم المركبة')
        ws.write(4, 1, req.vehicle_id.name if req.vehicle_id else '')
        ws.write(5, 0, 'نوع السيارة')
        ws.write(5, 1, req.vehicle_type or '')
        ws.write(6, 0, 'اسم السائق')
        ws.write(6, 1, req.driver_id.name if req.driver_id else '')

        row = 8
        ws.write(row, 0, 'القطعة')
        ws.write(row, 1, 'الكمية')
        ws.write(row, 2, 'السعر')
        ws.write(row, 3, 'الإجمالي')
        row += 1

        for line in req.part_line_ids:
            ws.write(row, 0, line.product_id.display_name)
            ws.write(row, 1, line.quantity)
            ws.write(row, 2, line.price_unit)
            ws.write(row, 3, line.price_subtotal)
            row += 1

        workbook.close()
        output.seek(0)
        filename = f"maintenance_request_{req.name.replace(' ', '_')}.xlsx"
        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ]
        return request.make_response(output.read(), headers=headers)
