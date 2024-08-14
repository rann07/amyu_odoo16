from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee Profile"

    no_time_required = fields.Boolean(string="No Time Required")
    ot_allowed = fields.Boolean(string="Allowed to Overtime")
    assigned_to_obu = fields.Many2one(string="Work Location", comodel_name="res.company",
                                      default=lambda self: self.env.company.id, required=True)
