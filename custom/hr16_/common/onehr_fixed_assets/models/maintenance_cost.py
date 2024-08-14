from odoo import fields, models


class MaintenanceCost(models.Model):
    _name = "maintenance.cost"
    _description = "Maintenance Costs"

    name = fields.Char(string="Description", required=True)
    amount = fields.Float(string="Cost")
    mr_id = fields.Many2one(string="Request Number", comodel_name="maintenance.request")
    cost_type_id = fields.Many2one(string="Type", comodel_name="maintenance.cost.type", required=True)
    equipment_name = fields.Char(string="Equipment", related="mr_id.equipment_id.name")


class MaintenanceCostType(models.Model):
    _name = "maintenance.cost.type"
    _description = "Maintenance Cost Type"

    name = fields.Char(string="Name", required=True)
