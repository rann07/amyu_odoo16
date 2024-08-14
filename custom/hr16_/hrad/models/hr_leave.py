from odoo import api, fields, models


class HrLeaveType(models.Model):
    _name = 'hr.leave.type'
    _description = 'HR Leave Types'

    name = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)
    with_annual_allocation = fields.Boolean(string="With Annual Allocation", default=False)
    active = fields.Boolean(string="Active", default=True)

    def name_get(self):
        result = []
        for log in self:
            name = "[" + str(log.name) + "] " + str(log.description)
            result.append((log.id, name))
        return result
