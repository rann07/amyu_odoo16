from odoo import fields, models


class PHTable(models.Model):
    _name = "philhealth.table"
    _description = "Philhealth Contributions Table"

    salfrom = fields.Float(string='Salary Range: From', required=True)
    salto = fields.Float(string='Salary Range: To', required=True)
    empshare = fields.Float(string='Employee Share', required=True)
    emprshare = fields.Float(string='Employer Share', required=True)
