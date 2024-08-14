from odoo import api, fields, models
from datetime import datetime
import requests
import base64


class HROvertime(models.Model):
    _name = "hr.filed.overtime"
    _description = "Filed Overtime"

    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee",
                                     required=True, copy=False)
    ot_key = fields.Integer(string="Transiton key", copy=False)
    ot_date = fields.Date(string="Date", required=True, copy=False)
    ot_start = fields.Float(string="Start", required=True, copy=False)
    ot_end = fields.Float(string="End", required=True, copy=False)
    duration = fields.Float(string="Duration", compute="_compute_ot_duration")
    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 related="hr_employee_id.company_id", copy=False)
    department_id = fields.Many2one(string="Department", comodel_name="hr.department",
                                    related="hr_employee_id.department_id", store=True, copy=False)
    ot_reason = fields.Text(string="Reason", copy=False)
    status = fields.Selection(string="Status", selection=[
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    ], default='for_approval', copy=False)
    approved_from_app = fields.Boolean(copy=False)
    approved_from_app_by = fields.Many2one(string="OT Approved by", comodel_name="hr.all.employee", copy=False)
    approved_by = fields.Many2one(string="OT Approved by", comodel_name="res.users", copy=False)
    approved_stamp = fields.Datetime(copy=False)
    disapproved_from_app = fields.Boolean(copy=False)
    disapproved_from_app_by = fields.Many2one(string="OT Disapproved by", comodel_name="hr.all.employee", copy=False)
    disapproved_by = fields.Many2one(string="OT Disapproved by", comodel_name="res.users", copy=False)
    disapproved_stamp = fields.Datetime(copy=False)
    hr_batch_ot_id = fields.Many2one(string="Batch OT", comodel_name="hr.batch.ot.requests")
    image_1920 = fields.Char(compute="leave_get_employee_image")

    def leave_get_employee_image(self):
        for s in self:
            s.image_1920 = s.env['hr.employee'].search([('id', '=', s.hr_employee_id.id)]).image_1920

    @api.onchange("ot_start", "ot_end")
    def ot_changed(self):
        self._compute_ot_duration()

    def _compute_ot_duration(self):
        for ot in self:
            ot.duration = ot.ot_end - ot.ot_start

    def get_employee_image(self):
        for s in self:
            s.image_1920 = s.env['hr.employee'].search([('id', '=', s.hr_employee_id.id)]).image_1920

    def name_get(self):
        result = []
        for emp in self:
            name = str(emp.hr_employee_id.name) + " - " + str(emp.ot_date)
            result.append((emp.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            if 'conversion' in vals:
                vals['ot_date'] = datetime.strptime(str(vals['ot_date']), "%Y-%m-%d")
                tfrom = str(vals['ot_start']).split(':')
                t, fhours = divmod(float(tfrom[0]), 24)
                t, fminutes = divmod(float(tfrom[1]), 60)
                fminutes = fminutes / 60.0

                tto = str(vals['ot_end']).split(':')
                t, thours = divmod(float(tto[0]), 24)
                t, tminutes = divmod(float(tto[1]), 60)
                tminutes = tminutes / 60.0

                vals['ot_start'] = fhours + fminutes
                vals['ot_end'] = thours + tminutes

                vals.pop('conversion')

            res = super(HROvertime, self).create(vals)

            if res:
                approvers = registration_token = []
                employee = self.env['hr.employee'].search([('id', '=', vals['hr_employee_id'])])
                approver_id = self.env['hr.employee'].search(
                    [('id', 'in', [approvers.append(a.id) for a in employee.ot_approver_ids])])
                for approver in approver_id:
                    dev_obj = self.env['res.users.devices'].search([('user_id', '=', approver.user_id.id)])
                    employee_name = employee.name
                    if dev_obj:
                        for dev in dev_obj:
                            registration_token.append(dev.name)
                        params = {
                            'title': 'Overtime Application',
                            'body': employee_name + ' filed an overtime application',
                            'registration_token': registration_token,
                        }
                        self.env['hr.ob'].push_notification(params)
        return res

    def write(self, vals):
        res = super(HROvertime, self).write(vals)
        if 'status' in vals:
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
                        'title': 'Overtime Application',
                        'body': 'Your Overtime Application has been ' + vals['status'],
                        'registration_token': registration_token,
                    }
                    self.env['hr.ob'].push_notification(params)

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
