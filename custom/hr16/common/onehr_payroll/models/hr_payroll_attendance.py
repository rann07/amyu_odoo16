from odoo import fields, models, api


class PayrollTimeSheet(models.Model):
    _name = "hr.payroll.attendance"
    _description = "Payroll Timesheet"

    hr_payroll_transaction_id = fields.Many2one(string="Payroll Transaction", comodel_name="hr.payroll.attendance")
    required_time = fields.Float(string="Required Time")
    date = fields.Date(string='Date')
    time_in = fields.Float(string='IN')
    time_out = fields.Float(string='OUT')
    hrs_worked = fields.Float(string='Rendered Hours')
    reg_hours = fields.Float(string='Reg. Hours')
    late = fields.Float(string='Late')
    undertime = fields.Float(string='Undertime')
    ot = fields.Float(string='Reg OT')
    nh = fields.Float(string='NH')
    sh = fields.Float(string='SH')
    nhot = fields.Float(string='NH-OT')
    shot = fields.Float(string='SH-OT')
    rdot = fields.Float(string='RD-OT')
    absent = fields.Float(string='Absent')

    # leave of absence fields
    on_leave = fields.Boolean(string="On Leave")
    half_day_leave = fields.Boolean(string="Half-day")
    hr_leave_type_id = fields.Many2one(string="Leave Type", comodel_name="hr.leave.type")
    leave_qty = fields.Float(string="LOA", help="Leave of absence quantity")

    # holiday
    is_holiday = fields.Boolean(string="Is Holiday?")
    holiday_type = fields.Selection(string="Type", selection=[('nh', "National Holiday"), ('sh', "Special Holiday")])
    holiday_name = fields.Char(string="Holiday")
