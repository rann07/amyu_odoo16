from odoo import fields, models


class HrEmployeeLeaveReset(models.Model):
    _name = "hr.employee.leave.reset"
    _description = "Employee Leaves Reset Logs"

    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    old_balance = fields.Float(string="Balance before reset")
    new_balance = fields.Float(string="Balance after reset")
