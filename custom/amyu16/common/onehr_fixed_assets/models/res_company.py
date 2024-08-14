from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = "Companies / OBU"

    host_ip = fields.Char(string="Host/IP")
    db_name = fields.Char(string="Database")
    username = fields.Char(string="Super User Name")
    passwd = fields.Char(string="Password")
    has_one = fields.Boolean(string="Has ONe System")
