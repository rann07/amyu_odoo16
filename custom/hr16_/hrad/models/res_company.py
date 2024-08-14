from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    holiday_id = fields.Many2one(string="Business Unit", comodel_name="hr.declared.holiday")
    inet_host = fields.Char(string="iNet Crystal Clear Server")
    inet_folder = fields.Char(string="Report Folder Name")
