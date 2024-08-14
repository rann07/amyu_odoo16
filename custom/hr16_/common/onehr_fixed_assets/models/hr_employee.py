from odoo import fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    fa_ids = fields.One2many(string="Assigned FA", comodel_name="onehr.fixed.assets", inverse_name="hr_employee_id")
