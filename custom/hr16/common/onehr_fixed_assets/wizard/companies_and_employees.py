# -*- coding: utf-8 -*-
from odoo import tools
from odoo import fields, models


class Employees(models.Model):
    _name = 'onehr.fa.view.all.employees'
    _description = 'All Employees Lookup'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    name = fields.Char(string="Employee")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "onehr_fa_view_all_employees")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW onehr_fa_view_all_employees AS
      SELECT id, company_id, name FROM hr_employee WHERE active;""")


class Departments(models.Model):
    _name = 'onehr.fa.view.all.departments'
    _description = 'All Department Lookup'
    _auto = False

    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")
    name = fields.Char(string="Department")
    manager_id = fields.Many2one(string="Manager", comodel_name="onehr.fa.view.all.employees")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "onehr_fa_view_all_departments")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW onehr_fa_view_all_departments AS
      SELECT * FROM hr_department WHERE active;""")


class Companies(models.Model):
    _name = 'onehr.fa.view.all.companies'
    _description = 'All Companies Lookup'
    _auto = False

    name = fields.Char(string="Business Unit")
    has_one = fields.Boolean(string="Has ONe System")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "onehr_fa_view_all_companies")
        self.env.cr.execute("""
      CREATE OR REPLACE VIEW onehr_fa_view_all_companies AS
      SELECT id, name, has_one FROM res_company;""")
