from odoo import fields, models


class HrLoanType(models.Model):
    _name = "hr.loan.type"
    _description = "Loan Types"

    name = fields.Char(string="Name", required=True)
    db_key = fields.Integer(string="Transition Key")
    active = fields.Boolean(string="Active", default=True)
    care = fields.Boolean(string="C.A.R.E.", default=False)
    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id, required=True)
