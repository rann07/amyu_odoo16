from odoo import api, fields, models


class SSSTable(models.Model):
    _name = "sss.table"
    _description = "SSS Contribution Table"

    salfrom = fields.Float(string='Salary Range: From', required=True)
    salto = fields.Float(string='Salary Range: To', required=True)
    empshare = fields.Float(string='Employee Share', required=True)
    emprshare = fields.Float(string='Employer Share', required=True)
