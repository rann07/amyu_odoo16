from odoo import models, fields


class HrEmployeeEducation(models.Model):
    _name = "hr.employee.education"
    _description = "Employee's Educational Background"

    name = fields.Char(string="Course")
    level = fields.Selection(string="Level", selection=[
        ("postgrad", "Post-Grad"),
        ("college", "College"),
        ("vocational", "Vocational (TESDA)"),
        ("highschool", "High School"),
        ("elem", "Elementary")
    ])
    school = fields.Char(string="School")
    graduated = fields.Boolean(string="Graduated")
    year_grad = fields.Date(string="Year Graduated")
    awards = fields.Text(string="Awards")
    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    db_key = fields.Integer(string="Transition Key")
