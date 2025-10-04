 # -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################
from odoo import models, fields
from odoo.exceptions import ValidationError, UserError
import base64
import xlrd

class ImportTaskChecklist(models.TransientModel):
    _name = "task.import"
    _description = "Import Task Checklist"

    upload_file = fields.Binary('Import Excel File', required=True)

    def import_checklist(self):
        try:
            # Check if file is empty
            if not self.upload_file:
                raise ValidationError("No file uploaded. Please upload an Excel file.")
            
            # Decode and process the file
            file_data = base64.b64decode(self.upload_file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
            data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]

            # Remove header
            data.pop(0)

            # Count imported records
            for row in data:
                if len(row) == 1:
                    row = row[0].split(';')
                if len(row) >= 3:
                    self.create_checklist_line(row)
                   

        except Exception as e:
            # Handle any other exceptions (like data format issues)
            raise ValidationError(f"An error occurred: {str(e)}")

        return True

    def create_checklist_line(self, row):
        # Ensure stage exists or raise error
        stage = self.env['project.task.type'].search([('name', '=', row[2].strip())], limit=1)
        # Create the checklist record
        self.env['task.checklist'].create({
            'name': row[0],  # Name
            'description': row[1],  # Description
            'stage_id': stage and stage.id or False  # Stage
        })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
