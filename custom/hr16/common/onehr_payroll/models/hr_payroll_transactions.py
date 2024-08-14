from odoo import fields, models


class PayrollTransactions(models.Model):
    _name = "hr.payroll.transactions"
    _description = "Payroll Transactions"

    payroll_master_id = fields.Many2one(string="Payroll", comodel_name="hr.payroll.master")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    monthly_basic_pay = fields.Float(string="Monthly Basic Pay", readonly=True)
    daily_basic_pay = fields.Float(string="Daily Basic Pay",readonly=True)
    leave_day = fields.Float(string="Leave Days")
    leave_pay = fields.Float(string="Leave Pay")
    ot_hours = fields.Float(string="OT Hours")
    ot_pay = fields.Float(string="OT Pay")
    rd_ot_hours = fields.Float(string="RD-OT Hours")
    rd_ot_pay = fields.Float(string="RD-OT Pay")
    nh_hours = fields.Float(string="NH Hours")
    nh_pay = fields.Float(string="NH Pay")
    sh_hours = fields.Float(string="SH Hours")
    sh_pay = fields.Float(string="SH Pay")
    supplemental = fields.Float(string="Supplemental")
    cola = fields.Float(string="COLA")
    # deductions
    late_hours = fields.Float(string="Late Hours")
    late_ded = fields.Float(string="Late Deduction")
    undertime_hours = fields.Float(string="Undertime Hours")
    undertime_ded = fields.Float(string="Undertime Deduction")
    absent_days = fields.Float(string="Absent Days")
    absent_ded = fields.Float(string="Absent Deduction")
    # miscellaneous
    allow_misc = fields.Float(string="Miscellaneous")
    allow_meal = fields.Float(string="Meal")
    allow_transpo = fields.Float(string="Transportation")
    # computed fields
    gross_pay = fields.Float(string="Gross Pay")
    deductions = fields.Float(string="Deductions")
    net_pay = fields.Float(string="Net Pay")

    # timesheet
    hr_payroll_attendance_ids = fields.One2many(string="Timesheet", comodel_name="hr.payroll.attendance",
                                                inverse_name="hr_payroll_transaction_id")
