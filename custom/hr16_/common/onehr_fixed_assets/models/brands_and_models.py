from odoo import fields, models


class Brand(models.Model):
    _name = "onehr.fa.fleet.make"
    _description = "Brand/Make"
    _sql_constraints = [("unique_fa_fleet_make", "unique(name)",
                         "Uniqueness of Brand/Make has been violated. Please choose different Make"), ]

    name = fields.Char(string="Brand/Make", required=True)
    make_ids = fields.One2many(string="Models", comodel_name="onehr.fa.fleet.model", inverse_name="make_id")


class Model(models.Model):
    _name = "onehr.fa.fleet.model"
    _description = "Model"
    _sql_constraints = [("unique_fa_fleet_model", "unique(make_id, name)",
                         "Uniqueness of Model has been violated. Please choose different Model"), ]

    make_id = fields.Many2one(string="Brand/Make", comodel_name="onehr.fa.fleet.make")
    name = fields.Char(string="Model", required=True)

    def name_get(self):
        result = []
        for m in self:
            name = str(m.make_id.name) + " - " + str(m.name)
            result.append((m.id, name))
        return result
