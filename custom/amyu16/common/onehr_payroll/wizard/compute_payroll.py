from odoo import fields, models
import datetime, calendar

YEARS = [('2023', '2023')]


class ComputePayroll(models.TransientModel):
    _name = "compute.payroll"

    month_of = fields.Selection(string="Month", selection=[
        ('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'),
        ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'Semptember'),
        ('October', 'October'), ('November', 'November'), ('December', 'December'),
    ], required=True, default=lambda self: calendar.month_name[datetime.date.today().month])
    year_of = fields.Selection(string="Year", selection=YEARS, required=True,
                               default=lambda self: str(datetime.date.today().year))
    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)

    def init(self):
        curr_year = datetime.date.today().year
        for n in range(curr_year - 2023):
            YEARS.append((str(2023 + n), str(2023 + n)))

    def action_compute_payroll(self):
        computed = self.compute_payroll()
        success = False
        if computed:
            success = {
                "name": "Computed Payroll: " + computed.name,
                "type": "ir.actions.act_window",
                "res_model": "hr.payroll.master",
                "views": [[self.env.ref("onehr_payroll.hr_payroll_master_tree").id, "tree"]],
                "domain": [('id', '=', computed.id)],
            }
            # self.post_attendance(hr_payroll_master_id=computed.id)
        return success

    def compute_payroll(self):
        name = "NE-" + self.year_of + "-" + str(self.month_of).upper()[0:3]
        executives = False
        month_of = self.month_of
        year_of = self.year_of
        from_date = self.from_date
        to_date = self.to_date
        res = self.env['hr.payroll.master'].create({
            'name': name,
            'executives': executives,
            'month_of': month_of,
            'year_of': year_of,
            'from_date': from_date,
            'to_date': to_date
        })

        if res:
            employees = self.env['hr.employee'].search([
                ('company_id', '=', self.env.company.id), ('active', '=', True), ('executive', '=', False)])
            for employee in employees:
                pt = {'payroll_master_id': res.id, 'hr_employee_id': employee.id}
                pt_res = self.env['hr.payroll.transactions'].create(pt)
                if pt_res:
                    print(self.env['hr.payroll.transactions'].browse(pt_res.id).id,pt_res.id)
                    self.env['hr.payroll.attendance'].create({'hr_payroll_transaction_id': pt_res.id})
                    monthly_basic_pay = employee.semi_monthly_rate if employee.pay_type == 'monthly' else 0
                    allow_misc = employee.allow_misc
                    allow_meal = employee.allow_meal
                    allow_transpo = employee.allow_transpo
                    daily_basic_pay = leave_day = leave_pay = ot_hours = ot_pay = rd_ot_hours = rd_ot_pay = nh_hours = \
                        nh_pay = sh_hours = sh_pay = supplemental = cola = late_hours = late_ded = undertime_hours = \
                        undertime_ded = absent_days = absent_ded = gross_pay = deductions = net_pay = 0
                    tc_obj = self.env['hr.time.card'].search([
                        ('hr_employee_id', '=', employee.id), ('date', '>=', self.from_date),
                        ('date', '<=', self.to_date)
                    ], order='date')
                    for tc in tc_obj:
                        # compute daily pay/deduction based on attendance
                        daily_basic_pay += employee.daily_rate if employee.pay_type == 'daily' and tc.absent == 0 else 0

                        absent_days += tc.absent
                        absent_ded += employee.daily_rate * tc.absent

                        leave_day += tc.leave_qty
                        leave_pay += tc.leave_qty * employee.daily_rate

                        monthly_basic_pay -= tc.leave_qty * employee.daily_rate if employee.pay_type == 'monthly' else 0
                        daily_basic_pay -= tc.leave_qty * employee.daily_rate if employee.pay_type == 'daily' else 0

                        cola += employee.daily_cola if tc.absent == 0 else 0

                        late_hours += tc.late
                        late_ded += tc.late * employee.hourly_rate
                        undertime_hours += tc.undertime
                        undertime_ded += tc.undertime * employee.hourly_rate
                        ot_hours += tc.ot
                        ot_pay += (employee.hourly_rate * 1.25) * tc.ot
                        rd_ot_hours += tc.rdot
                        rd_ot_pay += (employee.hourly_rate * 1.3) * tc.rdot

                        sh_hours += tc.sh
                        sh_pay += (employee.hourly_rate * 1.3) * tc.sh

                        nh_hours += tc.nh
                        nh_pay += (employee.hourly_rate * 2) * tc.nh

                    gross_pay = (monthly_basic_pay + ot_pay + rd_ot_pay + sh_pay + nh_pay + cola + allow_meal + \
                                 allow_misc + allow_transpo)
                    deductions = late_ded + undertime_ded + leave_pay + absent_ded
                    net_pay = gross_pay - deductions
                    pt_res.write({
                        'monthly_basic_pay': monthly_basic_pay, 'daily_basic_pay': daily_basic_pay,
                        'leave_day': leave_day, 'leave_pay': leave_pay,
                        'ot_hours': ot_hours, 'ot_pay': ot_pay,
                        'rd_ot_hours': rd_ot_hours, 'rd_ot_pay': rd_ot_pay,
                        'nh_hours': nh_hours, 'nh_pay': nh_pay,
                        'sh_hours': sh_hours, 'sh_pay': sh_pay,
                        'supplemental': supplemental, 'cola': cola,
                        'late_hours': late_hours, 'late_ded': late_ded,
                        'undertime_hours': undertime_hours, 'undertime_ded': undertime_ded,
                        'absent_days': absent_days, 'absent_ded': absent_ded,
                        'allow_misc': allow_misc, 'allow_meal': allow_meal, 'allow_transpo': allow_transpo,
                        'gross_pay': gross_pay, 'deductions': deductions, 'net_pay': net_pay
                    })

            return res

    def post_attendance(self, hr_payroll_master_id=False):
        if hr_payroll_master_id:
            payroll_transactions_obj = self.env['hr.payroll.transactions'].search([
                ('payroll_master_id', '=', hr_payroll_master_id)])
            for transaction in payroll_transactions_obj:
                tc_obj = self.env['hr.time.card'].search([
                    ('hr_employee_id', '=', transaction.hr_employee_id.id), ('date', '>=', self.from_date),
                    ('date', '<=', self.to_date)
                ], order='date')
                for tc in tc_obj:
                    vals = {'hr_payroll_transaction_id': transaction.id,
                            'required_time': tc.required_time,
                            'date': tc.date,
                            'time_in': tc.time_in,
                            'time_out': tc.time_out,
                            'hrs_worked': tc.hrs_worked,
                            'reg_hours': tc.reg_hours,
                            'late': tc.late,
                            'undertime': tc.undertime,
                            'ot': tc.ot,
                            'nh': tc.nh,
                            'sh': tc.sh,
                            'nhot': tc.nhot,
                            'shot': tc.shot,
                            'rdot': tc.rdot,
                            'absent': tc.absent,
                            'on_leave': tc.on_leave,
                            'half_day_leave': tc.half_day_leave,
                            'hr_leave_type_id': tc.hr_leave_type_id,
                            'leave_qty': tc.leave_qty,
                            'is_holiday': tc.is_holiday,
                            'holiday_type': tc.holiday_type,
                            'holiday_name': tc.holiday_name}
                    print(vals)
                    self.env['hr.payroll.attendance'].create(vals)
        return
