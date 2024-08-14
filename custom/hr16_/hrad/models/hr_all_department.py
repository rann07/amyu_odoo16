from odoo import fields, models, tools


class Employees(models.Model):
    _name = 'hr.all.department'
    _description = 'All Department List'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    name = fields.Char(string="Department")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_all_department")
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW hr_all_department AS
                SELECT * FROM hr_department WHERE active ORDER BY name;
      """)
