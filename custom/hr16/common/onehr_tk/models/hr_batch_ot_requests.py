from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HRBatchOTReq(models.Model):
    _name = "hr.batch.ot.requests"
    _description = "Batch Overtime Requests"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    name = fields.Char(string="Batch OT Control #", copy=False)
    hr_department_id = fields.Many2one(comodel_name="hr.department",
                                       string="Department", required=True, copy=False)
    user_id = fields.Many2one(comodel_name="res.users",
                              default=lambda self: self.env.user.id,
                              string="Prepared by", required=True, copy=False)
    date = fields.Datetime(string="Date", required=True)
    ot_start = fields.Float(string="From", required=True)
    ot_end = fields.Float(string="To", required=True)
    ot_reason = fields.Text(string="Reason", copy=False)
    status = fields.Selection(string="Status", selection=[
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved')
    ], default="for_approval", copy=False)
    approved_from_app = fields.Boolean(copy=False)
    approved_from_app_by = fields.Many2one(string="OT Approved by", comodel_name="res.users", copy=False)
    approved_by = fields.Many2one(string="OT Approved by", comodel_name="res.users", copy=False)
    approved_stamp = fields.Datetime(copy=False)
    disapproved_by = fields.Many2one(string="OT Disapproved by", comodel_name="res.users", copy=False)
    disapproved_stamp = fields.Datetime(copy=False)
    duration = fields.Float(string="Duration", compute="_compute_ot_duration")
    hr_employee_ids = fields.Many2many("hr.employee", string="Employees", required=True)

    def _compute_ot_duration(self):
        for r in self:
            r.duration = r.ot_end - r.ot_start

    def post_batch_ot_approve(self):
        for r in self.hr_employee_ids:
            fot_obj = self.env['hr.filed.overtime']
            fot_obj.create({
                'hr_employee_id': r.id,
                'ot_date': self.date,
                'ot_start': self.ot_start,
                'ot_end': self.ot_end,
                'hr_batch_ot_id': self.id,
                'status': 'approved',
                'approved_by': self.env.user.id,
                'approved_stamp': fields.Datetime.now()
            })
        self.write({
            'status': 'approved',
            'approved_by': self.env.user.id,
            'approved_stamp': fields.Datetime.now()
        })

    def post_batch_ot_disapprove(self):
        self.write({
            'status': 'disapproved',
            'disapproved_by': self.env.user.id,
            'disapproved_stamp': fields.Datetime.now()
        })

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            name = self.env['ir.sequence'].next_by_code('batch.ot.seq')
            vals.update({'name': name, 'status': 'for_approval'})
            res = super(HRBatchOTReq, self).create(vals)
        return res
