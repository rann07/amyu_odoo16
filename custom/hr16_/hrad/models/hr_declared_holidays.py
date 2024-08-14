from odoo import fields, models, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError


class HRDeclaredHolidays(models.Model):
    _name = "hr.declared.holiday"
    _description = "Declared Holidays"
    _sql_constraints = [('holiday_unique', 'unique(date,type)', 'Declared Holiday already exists!')]

    name = fields.Char(string="Title", required=True)
    date = fields.Date(string="Date", required=True)
    type = fields.Selection(string="Type", selection=[
        ('nh', "National Holiday"),
        ('sh', "Special Holiday")
    ], required=True, default="nh")
    company_ids = fields.One2many(string="Business Units", comodel_name="res.company", inverse_name="holiday_id")

    def is_holiday(self, h_date=False, company_id=False):
        is_holiday = False
        if date:
            holidays = self.search([('date', '=', h_date)])
            if holidays:
                for holiday in holidays:
                    if holiday.type == 'nh':
                        is_holiday = [holiday.type, holiday.name]
                    else:
                        for c_id in holiday.company_ids:
                            if c_id.id == company_id:
                                is_holiday = [holiday.type, holiday.name]
        return is_holiday
