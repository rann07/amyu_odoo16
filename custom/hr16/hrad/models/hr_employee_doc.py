from odoo import models, fields


class EmployeeDoc(models.Model):
    _inherit = "hr.employee.document"
    _description = "Employee Documents"

    document = fields.Binary(string="Document File", required=True)
