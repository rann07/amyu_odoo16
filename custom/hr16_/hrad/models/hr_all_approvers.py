from odoo import fields, models, tools


class Employees(models.Model):
    _name = 'hr.approvers'
    _description = 'HR Approvers List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    name = fields.Char(string="Approver")

    def name_get(self):
        result = []
        for e in self:
            name = str(e.name) + " - " + str(e.company_id.name)
            result.append((e.id, name))
        return result

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_approvers")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW hr_approvers AS
      SELECT id, company_id, name FROM hr_employee WHERE active AND executive ORDER BY name;""")
