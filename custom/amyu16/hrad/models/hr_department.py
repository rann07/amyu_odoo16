from odoo import api, fields, models


class HrDepartments(models.Model):
    _inherit = "hr.department"

    db_key = fields.Integer(string="Transition Key")
