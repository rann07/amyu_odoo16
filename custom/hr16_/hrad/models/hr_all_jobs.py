from odoo import fields, models, tools


class Employees(models.Model):
    _name = 'hr.all.job'
    _description = 'All Employee List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    name = fields.Char(string="Employee Name")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_all_employee")
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW hr_all_job AS
                SELECT * FROM hr_job WHERE active ORDER BY name;
      """)
