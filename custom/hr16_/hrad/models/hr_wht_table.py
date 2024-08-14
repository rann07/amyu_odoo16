from odoo import fields, models


class HrWhtTable(models.Model):
    _name = "hr.wht.table"
    _description = "Withholding Tax Table"

    name = fields.Selection(string="Tax Code", required=True, selection=[
        ("ME1/HF1", "ME1/HF1"), ("ME2/HF2", "ME2/HF2"),
        ("ME3/HF3", "ME3/HF3"), ("ME4/HF4", "ME4/HF4"),
        ("S/HF/ME", "S/HF/ME"), ("Z", "Z")])
    wht_type = fields.Selection(string="Schedules", default="3", selection=[
        ("1", "Daily"), ("2", "Weekly"),
        ("3", "Semi-monthly"), ("4", "Monthly")])
    base = fields.Float(string="Tax Base")
    wht = fields.Float(string="WHT")
    excess = fields.Float(string="(%) in excess")
