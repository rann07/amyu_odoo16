from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    fa_code = fields.Char(string="FA Code", related="equipment_id.fa_id.name")
    short_description = fields.Char(string="Short Description", related="equipment_id.fa_id.short_description")
    assigned_to = fields.Char(string="Custodian", related="equipment_id.fa_id.assigned_to")
    stage_stamp = fields.Datetime(string="Stage Stamp")
    cost_ids = fields.One2many(string="Costs", comodel_name="maintenance.cost", inverse_name="mr_id")
    maintenance_cost = fields.Float(string="Total Cost", compute="compute_cost", readonly=True)
    odometer_reading = fields.Float(string="Odometer Reading")

    def compute_cost(self):
        cost = 0
        for l in self.cost_ids:
            cost += l.amount
        self.maintenance_cost = cost

    def write(self, vals):
        if 'stage_id' in vals:
            vals.update({'stage_stamp': fields.Datetime.now()})
        res = super(MaintenanceRequest, self).write(vals)
        return res
