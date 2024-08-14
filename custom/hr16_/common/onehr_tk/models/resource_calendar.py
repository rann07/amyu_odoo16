from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"
    _description = "Resource Calendar"

    late_allowance = fields.Float(string="Late Allowance")
