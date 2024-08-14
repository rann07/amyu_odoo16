from odoo import fields, models, tools


class LeaveSubordinates(models.Model):
    _name = 'hr.leave.approver.subordinates'
    _description = 'HR Leave Approvers Subordinates List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.all.employee", required=True)
    hr_approver_id = fields.Many2one(string="Employee", comodel_name="hr.all.employee", required=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_leave_approver_subordinates")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW hr_leave_approver_subordinates AS
      SELECT b.id, a.hr_employee_id, a.hr_approver_id from
        hr_employee_leave_approvers_rel a left join hr_employee b on a.hr_employee_id = b.id;""")


class OtSubordinates(models.Model):
    _name = 'hr.ot.approver.subordinates'
    _description = 'HR OT Approvers Subordinates List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.all.employee", required=True)
    hr_approver_id = fields.Many2one(string="Employee", comodel_name="hr.all.employee", required=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_ot_approver_subordinates")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW hr_ot_approver_subordinates AS
      SELECT b.id, a.hr_employee_id, a.hr_approver_id from
        hr_employee_ot_approvers_rel a left join hr_employee b on a.hr_employee_id = b.id;""")


class ObSubordinates(models.Model):
    _name = 'hr.ob.approver.subordinates'
    _description = 'HR OB Approvers Subordinates List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.all.employee", required=True)
    hr_approver_id = fields.Many2one(string="Employee", comodel_name="hr.all.employee", required=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_ob_approver_subordinates")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW hr_ob_approver_subordinates AS
      SELECT b.id, a.hr_employee_id, a.hr_approver_id from
        hr_employee_ob_approvers_rel a left join hr_employee b on a.hr_employee_id = b.id;""")
