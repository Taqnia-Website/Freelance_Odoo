from odoo import http
from odoo.http import request
import io
import xlsxwriter
from datetime import datetime

class HrExcelExport(http.Controller):

    @http.route(['/hr_custom_ar/payroll_sheet/xlsx/<int:sheet_id>'], type='http', auth='user')
    def payroll_sheet_xlsx(self, sheet_id, **kw):
        sheet = request.env['hr.payroll.sheet'].browse(sheet_id).sudo()
        # Create xlsx in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet('كشف الرواتب')
        headers = ['الموظف','الراتب الأساسي','السلف','الخصومات','الإضافي','الصافي']
        for c, h in enumerate(headers):
            ws.write(0, c, h)
        row = 1
        for line in sheet.line_ids:
            ws.write(row,0,line.employee_id.name or '')
            ws.write(row,1,line.basic_salary or 0.0)
            ws.write(row,2,line.loan_total or 0.0)
            ws.write(row,3,line.deduction_total or 0.0)
            ws.write(row,4,line.overtime_total or 0.0)
            ws.write(row,5,line.net_salary or 0.0)
            row += 1
        workbook.close()
        output.seek(0)
        filename = f"payroll_sheet_{sheet.name.replace(' ','_')}.xlsx"
        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ]
        return request.make_response(output.read(), headers=headers)