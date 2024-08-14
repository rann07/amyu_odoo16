from odoo import models, fields


class HrMobileNotifications(models.Model):
    _name = 'hr.mobile.notifications'
    _description = 'HR Mobile Notifications'

    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True)
    notification_read = fields.Boolean(string="Read", default=False)

