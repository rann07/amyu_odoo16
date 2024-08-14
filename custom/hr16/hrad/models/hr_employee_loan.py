from odoo import fields, models


class HrEmployeeLoan(models.Model):
    _name = "hr.employee.loan"
    _description = "Employee's Loan Ledger"

    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id, required=True, copy=False)
    hr_loan_type_id = fields.Many2one(string="Loan Type", comodel_name="hr.loan.type", required=True, copy=False)
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True, copy=False)
    date_granted = fields.Date(string="Date Granted", required=True, copy=False)
    date_start = fields.Date(string="Start of deduction", required=True, copy=False)
    date_end = fields.Date(string="End of deduction")
    deductions_count = fields.Integer(string="Deductions count")
    deductions_per_payroll = fields.Float(string="Deduction per payroll")
    remaining_balance = fields.Float(string="Remaining balance")
    ref = fields.Char(string="Ref. doc.")
    quantity = fields.Integer(string="Quantity")
    description = fields.Char(string="Description")
    active = fields.Boolean(string="Active", default=True)

    def name_get(self):
        result = []
        for cat in self:
            name = str(cat.hr_loan_type_id.name) + " [" + str(cat.hr_employee_id.name) + "]"
            result.append((cat.id, name))
        return result
