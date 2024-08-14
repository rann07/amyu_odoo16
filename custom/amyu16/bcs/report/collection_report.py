from odoo import models

class PartnerXlsx(models.AbstractModel):
    _name = 'report.bcs.collection_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # report_name = obj.name
        sheet = workbook.add_worksheet('Report')
        bold = workbook.add_format({'font_size': 12})
        
        sheet.write(0, 0, obj.name, bold)