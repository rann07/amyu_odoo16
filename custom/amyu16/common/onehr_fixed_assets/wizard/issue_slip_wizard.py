from odoo import fields, models
from datetime import date, datetime


class IssueSlip(models.TransientModel):
    _name = "print.issue.slip"
    _description = "Print Issue Slip"
    _inherit = "onehr.fixed.assets"

    fa_id = fields.Many2one(string="Fixed Assets ID", comodel_name="onehr.fixed.assets")
    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    name = fields.Char(string="Asset Code")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    hr_department_id = fields.Many2one(string="Department", comodel_name="hr.department")
    print_date = fields.Date(string="Print Date", required=True, default=datetime.today())

    def print_issue_slip(self):
        date_today = datetime.today()
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        company_obj = self.env.company
        inet_host = company_obj.inet_host
        inet_folder = company_obj.inet_folder
        user = str(self.env.user.name)

        if len(ids) > 1 or self.print_date is False:
            pd = str(date_today.strftime('%Y,%m,%d'))
            current_company = str(self.env.company.id)
        else:
            pd = str(self.print_date.strftime('%Y,%m,%d'))
            current_company = str(self.company_id.id)

        url = inet_host + "/?report=" + inet_folder + \
              "/issue_slip.rpt&init=pdf&prompt0=" + str(ids) + \
              "&prompt1=date(" + pd + ")" + \
              "&prompt2=" + user.upper() + \
              "&prompt3=" + current_company

        return {'name': 'Fixed Assets Issue Slip',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': url
                }
