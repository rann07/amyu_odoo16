from odoo import fields, models, api
import base64, requests


class HrEmployeeLeaveTransaction(models.Model):
    _name = "hr.employee.leave.transaction"
    _description = "Employee's Filed Leave"

    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    name = fields.Char(string="Document Number")
    hr_leave_type_id = fields.Many2one(string="Leave Type", comodel_name="hr.leave.type", required=True)
    hr_employee_id = fields.Many2one(string="Employee Name", comodel_name="hr.all.employee", required=True)
    job_name = fields.Char(string="Job Position", related="hr_employee_id.job_id.name", readonly=True, store=True)
    department_name = fields.Char(string="Department", related="hr_employee_id.department_id.name", readonly=True,
                                  store=True)
    start_date = fields.Date(string="Start Date", required=True, default=fields.Date.today())
    end_date = fields.Date(string="End Date", default=fields.Date.today())
    half_day = fields.Boolean(string="Half-day", default=False)
    reason = fields.Text(string="Reason", required=True)
    status = fields.Selection(string="Status", default='for_approval', selection=[
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved')
    ])
    approved_from_app = fields.Boolean()
    approved_from_app_by = fields.Many2one(string="Leave Approved by", comodel_name="hr.all.employee")
    approved_by = fields.Many2one(string="Leave Approved by", comodel_name="res.users")
    approved_stamp = fields.Datetime()
    disapproved_from_app = fields.Boolean()
    disapproved_from_app_by = fields.Many2one(string="Leave Disapproved by", comodel_name="hr.all.employee")
    disapproved_by = fields.Many2one(string="Leave Disapproved by", comodel_name="res.users")
    disapproved_stamp = fields.Datetime()
    image_1920 = fields.Char(compute="leave_get_employee_image")

    def leave_get_employee_image(self):
        for s in self:
            s.image_1920 = s.env['hr.employee'].search([('id', '=', s.hr_employee_id.id)]).image_1920

    # @api.model_write_multi
    def write(self, vals):
        res = super(HrEmployeeLeaveTransaction, self).write(vals)

        if res:
            registration_token = []
            employee = self.env['hr.employee'].search([('id', '=', self.hr_employee_id.id)])
            dev_obj = self.env['res.users.devices'].search([('user_id', '=', employee.user_id.id)])

            employee_name = employee.name
            if dev_obj:
                for dev in dev_obj:
                    registration_token.append(dev.name)
                    print(dev)

                params = {
                    'title': self.hr_leave_type_id.description + ' Application',
                    'body': 'Your ' + self.hr_leave_type_id.description + ' Application has been ' + vals['status'],
                    'registration_token': registration_token,
                }
                self.env['hr.ob'].push_notification(params)

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            if 'company_id' not in vals:
                vals.update({'company_id': self.env['hr.employee'].browse([vals['hr_employee_id']]).company_id.id})
            vals.update({'name': self.env['ir.sequence'].next_by_code('leave.seq')})
            res = super(HrEmployeeLeaveTransaction, self).create(vals)

            if res:
                approvers = registration_token = []
                employee = self.env['hr.employee'].search([('id', '=', vals['hr_employee_id'])])
                approver_id = self.env['hr.employee'].search(
                    [('id', 'in', [approvers.append(a.id) for a in employee.ot_approver_ids])])
                for approver in approver_id:
                    dev_obj = self.env['res.users.devices'].search([('user_id', '=', approver.user_id.id)])
                    leave_type = self.env['hr.leave.type'].search([('id', '=', vals['hr_leave_type_id'])])
                    employee_name = employee.name
                    if dev_obj:
                        for dev in dev_obj:
                            registration_token.append(dev.name)
                            print(dev)

                        params = {
                            'title': leave_type.description + ' Application',
                            'body': employee_name + ' filed a ' + leave_type.description + ' application',
                            'registration_token': registration_token,
                        }
                        self.env['hr.ob'].push_notification(params)
        return res

    def action_approved(self):
        self.write({
            'status': 'approved',
            'approved_by': self.env.user.id,
            'approved_stamp': fields.Datetime.now()
        })

    def action_disapproved(self):
        self.write({
            'status': 'disapproved',
            'disapproved_by': self.env.user.id,
            'disapproved_stamp': fields.Datetime.now()
        })

    @api.onchange("start_date", "end_date")
    def date_change(self):
        if self.end_date < self.start_date:
            self.end_date = self.start_date
