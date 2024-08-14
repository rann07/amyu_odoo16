from odoo import fields, models


class RatesHistory(models.Model):
    _name = "hr.employee.rates.history"
    _description = "Rates History"

    db_key = fields.Integer(string="Transition Key")
    monthly_rate = fields.Float(string="Monthly")
    semi_monthly_rate = fields.Float(string="Semi-monthly")
    weekly_rate = fields.Float(string="Weekly")
    daily_rate = fields.Float(string="Daily")
    hourly_rate = fields.Float(string="Hourly")
    monthly_cola = fields.Float(string="Monthly COLA")
    semi_monthly_cola = fields.Float(string="Semi-monthly COLA")
    weekly_cola = fields.Float(string="Weekly COLA")
    daily_cola = fields.Float(string="Daily COLA")
    hourly_cola = fields.Float(string="Hourly COLA")
    allow_misc = fields.Float(string="Miscellaneous")
    allow_meal = fields.Float(string="Meal")
    allow_transpo = fields.Float(string="Transpo")
    tm_monthly = fields.Float(string="Monthly TM")
    tm_semi_monthly = fields.Float(string="Semi-monthly TM")
    tm_weekly = fields.Float(string="Weekly TM")
    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    doe = fields.Date(string="Effectivity")
