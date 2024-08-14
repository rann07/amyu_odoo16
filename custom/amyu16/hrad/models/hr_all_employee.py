from odoo import fields, models, tools


class Employees(models.Model):
    _name = 'hr.all.employee'
    _description = 'All Employee List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    name = fields.Char(string="Employee Name")
    department_id = fields.Many2one(string="Department", comodel_name="hr.all.department")
    job_id = fields.Many2one(string="Designation", comodel_name="hr.all.job")
    executive = fields.Boolean(string="Belongs to Executives")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_all_employee")
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW hr_all_employee AS
                SELECT id, company_id, department_id, job_id, executive, (family_name || ', ' || first_name) AS name 
                FROM hr_employee WHERE active ORDER BY name;
      """)
