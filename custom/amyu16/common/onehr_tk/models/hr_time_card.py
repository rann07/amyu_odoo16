from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class HRTimeCard(models.Model):
    _name = "hr.time.card"
    _description = "Time Card Data Entry"
    _sql_constraints = [("unique_time_card", "unique(hr_employee_id, date)",
                         "Uniqueness of attendance record has been violated. Please choose different date."), ]

    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True)
    job_name = fields.Char(string="Job Position", related="hr_employee_id.job_id.name", readonly=True, store=True)
    department_name = fields.Char(string="Department", related="hr_employee_id.department_id.name", readonly=True,
                                  store=True)
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    required_time = fields.Float(string="Required Time", readonly=True)
    date = fields.Date(string='Date', default=datetime.today(), required=True)
    time_in = fields.Float(string='IN', required=True)
    time_out = fields.Float(string='OUT', required=True)
    hrs_worked = fields.Float(string='Rendered Hours', readonly=True)
    reg_hours = fields.Float(string='Reg. Hours', readonly=True)
    late = fields.Float(string='Late', readonly=True)
    undertime = fields.Float(string='Undertime', readonly=True)
    ot = fields.Float(string='Reg OT', readonly=True)
    nh = fields.Float(string='NH', readonly=True)
    sh = fields.Float(string='SH', readonly=True)
    nhot = fields.Float(string='NH-OT', readonly=True)
    shot = fields.Float(string='SH-OT', readonly=True)
    rdot = fields.Float(string='RD-OT', readonly=True)
    absent = fields.Float(string='Absent', readonly=True)
    posted = fields.Boolean(string="Posted to Payroll", default=False)
    posted_stamp = fields.Datetime(string="Posted Stamp")

    # leave of absence fields
    on_leave = fields.Boolean(string="On Leave", default=False)
    half_day_leave = fields.Boolean(string="Half-day")
    hr_leave_type_id = fields.Many2one(string="Leave Type", comodel_name="hr.leave.type")
    leave_qty = fields.Float(string="LOA", help="Leave of absence quantity")

    # holiday
    is_holiday = fields.Boolean(string="Is Holiday?")
    holiday_type = fields.Selection(string="Type", selection=[('nh', "National Holiday"), ('sh', "Special Holiday")])
    holiday_name = fields.Char(string="Holiday")

    def name_get(self):
        result = []
        for emp in self:
            name = str(emp.hr_employee_id.name) + " - " + str(emp.date)
            result.append((emp.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            if 'company_id' not in vals:
                vals.update({'company_id': self.env['hr.employee'].browse([vals['hr_employee_id']]).company_id.id})
            res = super(HRTimeCard, self).create(vals)
        return res

    def compute_time_card(self, from_date=False, to_date=False, company_id=False):
        from_date = fields.Datetime.now().date() if not from_date else from_date
        to_date = fields.Datetime.now().date() if not to_date else to_date
        print("Computing time cards for the period", from_date, to_date)
        if not company_id:  # All Business Units to process
            obu_obj = self.env['res.company'].search([('active', '=', True)], order='name')
        else:
            obu_obj = self.env['res.company'].search([('id', '=', company_id)], order='name')
        for obu in obu_obj:
            print("Processing", obu.id, obu.name)
            employee_obj = self.env['hr.employee'].search([('company_id', '=', obu.id),
                                                           ('active', '=', True)], order="name")
            for employee in employee_obj:
                print("->", employee.name)
                delta = to_date - from_date
                # if delta.days >= 0:
                for n in range(delta.days + 1):
                    date = (from_date + timedelta(days=n))
                    required_time = time_in = time_out = hrs_worked = reg_hours = late = leave_qty = \
                        undertime = ot = nh = sh = nhot = shot = rdot = absent = 0
                    holiday_name = holiday_type = is_holiday = on_leave = half_day_leave = hr_leave_type_id = False
                    # get in and out from face id logs
                    in_out = self.get_in_out(hr_employee_id=employee.id, date=date)
                    time_in = float(in_out['time_in'])
                    time_out = float(in_out['time_out'])
                    tc_line = {'hr_employee_id': employee.id, 'date': date, 'time_in': time_in,
                               'time_out': time_out}

                    # Employee is time required. Perform date and time processing
                    res_cal_obj = self.env['resource.calendar'].browse([employee.resource_calendar_id.id])
                    if not res_cal_obj:
                        raise UserError(_(employee.name + " does not have work schedule set"))

                    work_sched = res_cal_obj.attendance_ids.search([
                        ('dayofweek', '=', date.weekday()),
                        ('calendar_id', '=', employee.resource_calendar_id.id)
                    ], limit=1)
                    if work_sched.id and not employee.no_time_required:
                        print("-->", date)
                        hour_from = work_sched.hour_from
                        hour_to = work_sched.hour_to
                        late_allowance = res_cal_obj.late_allowance
                        required_time = res_cal_obj.hours_per_day
                        hrs_worked = 0 if time_out == 0 or time_in == time_out else time_out - time_in
                        late = max(0, time_in - (hour_from + late_allowance))
                        undertime = max(0, hour_to - time_out)
                        reg_hours = max(0, min(hrs_worked, required_time) - late - undertime)

                        if time_in == time_out:
                            absent = 1
                            late = undertime = 0

                        holiday = self.get_holiday(date=date, company_id=employee.company_id.id)

                        if absent == required_time:
                            if holiday:
                                absent = late = reg_hours = required_time = 0
                            else:
                                leave_info = self.get_leave_info(hr_employee_id=employee.id, date=date)
                                if leave_info:
                                    absent = late = reg_hours = required_time = 0
                                    half_day_leave = leave_info['half_day']
                                    hr_leave_type_id = leave_info['hr_leave_type_id']
                                    on_leave = True
                                    leave_qty = 0.5 if half_day_leave else 1

                        ot_hours = self.get_overtime_requests(hr_employee_id=employee.id, date=date)
                        if holiday and time_in > 0 and time_out > 0:
                            late = reg_hours = required_time = 0
                            # check if there are approved overtime requests
                            if ot_hours > 0:
                                if holiday['type'] == 'sh':
                                    sh = ot_hours
                                else:
                                    nh = ot_hours
                        if not holiday and not required_time > 0 and ot_hours > 0:
                            ot = ot_hours
                    if not work_sched.id:
                        print("--->", date, "is", employee.name, "day off")
                        ot_hours = self.get_overtime_requests(hr_employee_id=employee.id, date=date)
                        if ot_hours > 0:
                            rdot = ot_hours
                    tc_line.update(
                        {'hrs_worked': hrs_worked, 'reg_hours': reg_hours, 'late': late, 'undertime': undertime,
                         'ot': ot, 'nh': nh, 'sh': sh, 'nhot': nhot, 'shot': shot, 'rdot': rdot,
                         'absent': absent, 'leave_qty': leave_qty, 'holiday_name': holiday_name,
                         'holiday_type': holiday_type, 'is_holiday': is_holiday, 'on_leave': on_leave,
                         'half_day_leave': half_day_leave, 'hr_leave_type_id': hr_leave_type_id,
                         'required_time': required_time
                         })
                    # get face id in and out from face id logs
                    tc_obj = (self.search([('hr_employee_id', '=', employee.id),
                                           ('date', '=', date)], limit=1))
                    if tc_obj.id:
                        tc_obj.write(tc_line)
                    else:
                        self.create(tc_line)

    def get_in_out(self, hr_employee_id=False, date=False):
        in_out = {'time_in': 0, 'time_out': 0}
        if hr_employee_id and date:
            # get first log from hr_faceid_logs model as "time_in"
            self.env.cr.execute("""
                    SELECT (to_char(log_stamp + '8 hours'::interval, 'HH24:MI')::TIME)::TEXT AS log_time
                    FROM hr_faceid_logs WHERE (log_stamp + '8 hours'::interval)::DATE = %s::DATE
                    AND hr_employee_id = %s ORDER BY log_stamp ASC LIMIT 1; 
                    """, (date, hr_employee_id))
            first_log = self.env.cr.fetchall()
            for f in first_log:
                log_time = f[0].split(':')
                t, hours = divmod(float(log_time[0]), 24)
                t, minutes = divmod(float(log_time[1]), 60)
                minutes = minutes / 60.0
                time_in = hours + minutes
                in_out.update({'time_in': time_in})
            # get last log from hr_faceid_logs model as "time_out"
            self.env.cr.execute("""
                    SELECT (to_char(log_stamp + '8 hours'::interval, 'HH24:MI')::TIME)::TEXT AS log_time
                    FROM hr_faceid_logs WHERE (log_stamp + '8 hours'::interval)::DATE = %s::DATE
                    AND hr_employee_id = %s ORDER BY log_stamp DESC LIMIT 1; 
                    """, (date, hr_employee_id))
            last_log = self.env.cr.fetchall()
            for l in last_log:
                log_time = l[0].split(':')
                t, hours = divmod(float(log_time[0]), 24)
                t, minutes = divmod(float(log_time[1]), 60)
                minutes = minutes / 60.0
                time_out = hours + minutes
                in_out.update({'time_out': time_out})
        return in_out

    def get_leave_info(self, hr_employee_id=False, date=False):
        leave_info = False
        if hr_employee_id and date:
            leave_obj = self.env['hr.employee.leave.transaction'].search([
                ('hr_employee_id', '=', hr_employee_id), ('status', '=', 'approved'),
                ('start_date', '>=', date), ('end_date', '>=', date)
            ])
            if leave_obj:
                for leave in leave_obj:
                    leave_info = {'hr_leave_type_id': leave.hr_leave_type_id.id, 'half_day': leave.half_day}
        return leave_info

    def get_overtime_requests(self, hr_employee_id=False, date=False):
        total_ot = 0
        if hr_employee_id and date:
            ot_requests = self.env['hr.filed.overtime'].search([
                ('hr_employee_id', '=', hr_employee_id),
                ('ot_date', '=', date), ('status', '=', 'approved')
            ])
            if ot_requests:
                for ot_request in ot_requests:
                    total_ot += ot_request.ot_end - ot_request.ot_start
                    if ot_request.ot_end >= 13:
                        total_ot -= 1
        return total_ot

    def get_holiday(self, date=False, company_id=False):
        holiday = False
        if date and company_id:
            holiday_obj = self.env['hr.declared.holiday'].search([('date', '=', date)])
            if holiday_obj:
                for h in holiday_obj:
                    holiday = {'name': h.name, 'type': h.type}
                    if h.type == 'sh':
                        company_in_selection = False
                        for c in h.company_ids:
                            company_in_selection = (c.id == company_id)
                        if not company_in_selection:
                            holiday = False
        return holiday


class HrAllTimeCard(models.Model):
    _name = 'hr.all.time.card'
    _description = 'All Employee Time Card'
    _auto = False

    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True)
    job_name = fields.Char(string="Job Position", related="hr_employee_id.job_id.name", readonly=True, store=True)
    department_name = fields.Char(string="Department", related="hr_employee_id.department_id.name", readonly=True,
                                  store=True)
    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 related="hr_employee_id.company_id", store=True)
    required_time = fields.Float(string="Required Time", readonly=True)
    date = fields.Date(string='Date', default=datetime.today(), required=True)
    time_in = fields.Float(string='IN', required=True)
    time_out = fields.Float(string='OUT')
    hrs_worked = fields.Float(string='Rendered Hours', readonly=True)
    reg_hours = fields.Float(string='Reg. Hours', readonly=True)
    late = fields.Float(string='late', readonly=True)
    undertime = fields.Float(string='Undertime', readonly=True)
    ot = fields.Float(string='Overtime', readonly=True)
    nh = fields.Float(string='NH', readonly=True)
    sh = fields.Float(string='SH', readonly=True)
    nhot = fields.Float(string='NH-OT', readonly=True)
    shot = fields.Float(string='SH-OT', readonly=True)
    rdot = fields.Float(string='RD-OT', readonly=True)
    absent = fields.Float(string='Absent', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_all_time_card")
        self.env.cr.execute("""
                    CREATE OR REPLACE VIEW hr_all_time_card AS
                        SELECT * FROM hr_time_card;;
              """)
