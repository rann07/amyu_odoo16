from odoo import api, fields, models
import base64, requests


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    family_name = fields.Char(string="Family Name")
    fullname = fields.Char(string="Full Name", compute="get_full_name")
    employee_id = fields.Char(string="Employee ID")
    employment_status = fields.Selection(string="Employment Status", selection=[
        ("cos", "Contract of Service"),
        ("probi", "Probational"),
        ("ojt", "O.J.T."),
        ("pb", "Project Base"),
        ("cb", "Commision Base"),
        ("regular", "Regular")
    ])
    executive = fields.Boolean(string="Belongs to Executives")
    executive_id = fields.Many2one(string="Executive", comodel_name="hr.all.employee",
                                   domain=[('executive', '=', True)])
    cos_date = fields.Date(string="CoS")
    cos_enddate = fields.Date(string="End-Date")
    probi_date = fields.Date(string="Probational")
    probi_enddate = fields.Date(string="End-Date")
    ojt_date = fields.Date(string="O.J.T.")
    ojt_enddate = fields.Date(string="End-Date")
    pb_date = fields.Date(string="Project Base")
    pb_enddate = fields.Date(string="End-Date")
    cb_date = fields.Date(string="Commission")
    cb_enddate = fields.Date(string="End-Date")
    date_regular = fields.Date(string="Date Regular")
    date_hired = fields.Date(string="Date Hired")
    # emergency_contact = fields.Text(string="Emergency Contact")
    db_key = fields.Integer(string="Transision Key")
    fathers_name = fields.Char(string="Father's Name")
    mothers_name = fields.Char(string="Mother's Name")
    mailing_address_is = fields.Selection(string="Mailing Address", selection=[
        ("a1", "Address 1"), ("a2", "Address 2")
    ])
    address1 = fields.Text(string="Address 1")
    address2 = fields.Text(string="Address 2")
    priv_email = fields.Char(string="Email")
    priv_phone = fields.Char(string="Contact Numbers")
    # identifications
    tax_code = fields.Selection(string="Tax Code", selection=[
        ("Z", "Z"),
        ("S/HF/ME", "S/HF/ME"),
        ("ME1/HF1", "ME1/HF1"),
        ("ME2/HF2", "ME2/HF2"),
        ("ME3/HF3", "ME3/HF3"),
        ("ME4/HF4", "ME4/HF4"),
    ])
    bank_account = fields.Char(string="Bank Account#")
    tin = fields.Char(string="T.I.N.")
    sss = fields.Char(string="S.S.S.")
    hdmf = fields.Char(string="Pag-IBIG")
    phic = fields.Char(string="PhilHealth")
    medicard = fields.Char(string="Medicard")
    medicard_active = fields.Boolean(string="Active")
    # specimen signature
    signature = fields.Binary(string="Signature")
    # compensation info
    monthly_rate = fields.Float(string="Monthly")
    semi_monthly_rate = fields.Float(string="Semi-monthly")
    weekly_rate = fields.Float(string="Weekly")
    daily_rate = fields.Float(string="Daily")
    hourly_rate = fields.Float(string="Hourly")
    monthly_cola = fields.Float(string="Monthly")
    semi_monthly_cola = fields.Float(string="Semi-monthly")
    weekly_cola = fields.Float(string="Weekly")
    daily_cola = fields.Float(string="Daily")
    hourly_cola = fields.Float(string="Hourly")
    allow_misc = fields.Float(string="Miscellaneous")
    allow_meal = fields.Float(string="Meal")
    allow_transpo = fields.Float(string="Transportation")
    tm_monthly = fields.Float(string="Monthly")
    tm_semi_monthly = fields.Float(string="Semi-monthly")
    tm_weekly = fields.Float(string="Weekly")
    ded_sss = fields.Boolean(string="S.S.S.")
    ded_phic = fields.Boolean(string="PhilHealth")
    ded_hdmf = fields.Boolean(string="H.D.M.F.")
    ded_phic_er = fields.Float(string="Employer")
    ded_phic_ee = fields.Float(string="Employee")
    pay_type = fields.Selection(string="Pay Type", selection=[
        ('daily', "Daily"), ("monthly", "Monthly")], default="daily")

    # rates history
    rates_history = fields.One2many(string="Rates History",
                                    comodel_name="hr.employee.rates.history", inverse_name="employee_id")
    # educational background
    employee_educ_ids = fields.One2many(string="Educational Background",
                                        comodel_name="hr.employee.education", inverse_name="employee_id")
    # other benefits
    ob_ids = fields.One2many(string="Other Benefits", comodel_name="hr.employee.ob",
                             inverse_name="employee_id")
    # Leave
    hr_leave_ids = fields.One2many(string="Leave Types", comodel_name="hr.employee.leave.master",
                                   inverse_name="hr_employee_id")

    # Approver
    leave_approver_ids = fields.Many2many("hr.approvers", "hr_employee_leave_approvers_rel",
                                          "hr_employee_id", "hr_approver_id", string='Leave')
    ob_approver_ids = fields.Many2many("hr.approvers", "hr_employee_ob_approvers_rel",
                                       "hr_employee_id", "hr_approver_id", string='Official Business')
    ot_approver_ids = fields.Many2many("hr.approvers", "hr_employee_ot_approvers_rel",
                                       "hr_employee_id", "hr_approver_id", string='Overtime')

    def get_full_name(self):
        self.fullname = (self.family_name or "").title() + ", " + \
                        (self.first_name or "").title() + " " + \
                        (self.middle_name or "").title()

    @api.depends("name")
    @api.onchange("first_name", "middle_name", "family_name")
    def full_name_changed(self):
        if self.first_name or self.middle_name or self.family_name:
            fname = (self.family_name or "").upper() + ", " + (self.first_name or "").upper()
            self.name = fname.title()
            self.first_name = (self.first_name or "").upper()
            self.middle_name = (self.middle_name or "").upper()
            self.family_name = (self.family_name or "").upper()
        return

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            fName = (vals['first_name'] or "") + \
                    " " + (vals['family_name'] or "").upper()
            vals['first_name'] = (vals['first_name'] or "").upper()
            vals['middle_name'] = (vals['middle_name'] or "").upper()
            vals['family_name'] = (vals['family_name'] or "").upper()
            if "name" in vals:
                vals['name'] = fName
            else:
                vals.update({'name': fName})
            res = super(HrEmployee, self).create(vals)
            if res:
                leaves_obj = self.env['hr.leave.type'].search([('active', '=', True)])
                for leave in leaves_obj:
                    leaves = {
                        'hr_employee_id': res.id,
                        'hr_leave_type_id': leave.id
                    }
                    self.env['hr.employee.leave.master'].create(leaves)
        return res

    def toggle_executive(self):
        self.executive = not self.executive
        return
