from odoo import http
from odoo.http import request
import io
import xlsxwriter

class PayrollXlsxController(http.Controller):

    @http.route('/hr_custom_ar/payroll_sheet/xlsx/<int:sheet_id>', type='http', auth='user')
    def export_payroll_xlsx(self, sheet_id, **kw):
        sheet = request.env['hr.payroll.sheet'].browse(sheet_id).sudo()
        if not sheet.exists():
            return request.not_found()

        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet('Payroll')

        headers = ['الموظف','الأساسي','السلف','الخصومات','الإضافي','الصافي']
        for col, h in enumerate(headers):
            ws.write(0, col, h)

        row = 1
        for line in sheet.line_ids:
            ws.write(row, 0, line.employee_id.name or '')
            ws.write(row, 1, line.basic_salary or 0.0)
            ws.write(row, 2, line.loan_total or 0.0)
            ws.write(row, 3, line.deduction_total or 0.0)
            ws.write(row, 4, line.overtime_total or 0.0)
            ws.write(row, 5, line.net_salary or 0.0)
            row += 1

        wb.close()
        output.seek(0)

        headers_http = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename=payroll_{sheet.id}.xlsx')
        ]
        return request.make_response(output.read(), headers=headers_http)
