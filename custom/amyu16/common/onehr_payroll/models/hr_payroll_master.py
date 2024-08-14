from odoo import fields, models


class PayrollMaster(models.Model):
    _name = "hr.payroll.master"
    _description = "Payroll Master"

    company_id = fields.Many2one(string="Company", comodel_name="res.company", required=True, copy=False,
                                 default=lambda self: self.env.company.id)
    name = fields.Char(string="Title")
    executives = fields.Boolean(string="Executives")
    month_of = fields.Char(string="Month")
    year_of = fields.Char(string="Year")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    hr_payroll_transaction_ids = fields.One2many(string="Payroll Breakdown", comodel_name="hr.payroll.transactions",
                                                 inverse_name="payroll_master_id")
