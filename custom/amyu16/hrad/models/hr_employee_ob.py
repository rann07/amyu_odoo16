from odoo import fields, models


class EmployeeOB(models.Model):
    _name = "hr.employee.ob"
    _description = "Employee's Other Benefits"

    db_key = fields.Integer(string="Transition Key")
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    status = fields.Selection(string="Status", selection=[
        ("active", "Active"),
        ("discontinued", "Discontinued"),
        ("revoked", "Revoked")
    ])
    amount = fields.Float(string="Amount")
    employee_id = fields.Many2one(string="Employee", required=True,
                                  comodel_name="hr.employee")
