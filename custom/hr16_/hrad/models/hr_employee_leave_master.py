from odoo import fields, models


class HrEmployeeLeaveMaster(models.Model):
    _name = "hr.employee.leave.master"
    _description = "Employee's Allowed Leave"
    _sql_constraints = [
        ('unique_employee_leave_master', 'unique (hr_leave_type_id,hr_employee_id)',
         'Leave Type must be unique per employee')
    ]

    hr_leave_type_id = fields.Many2one(string="Leave Type", comodel_name="hr.leave.type")
    with_annual_allocation = fields.Boolean(string="With Annual Allocation",
                                            related="hr_leave_type_id.with_annual_allocation", readonly=True)
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    current_balance = fields.Float(string="Current Balance")

    def show_leave_reset_logs(self):
        hr_employee_id = self.env.context.get('hr_employee_id')
        if hr_employee_id:
            return {
                'name': "Resetting of Leave Logs: " + self.hr_employee_id.name,
                'res_model': 'hr.employee.leave.reset',
                'type': 'ir.actions.act_window',
                'domain': [('hr_employee_id', '=', hr_employee_id)],
                'view_mode': 'tree',
                'target': 'new', }
