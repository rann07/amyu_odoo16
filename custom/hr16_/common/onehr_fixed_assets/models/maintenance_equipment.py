from odoo import fields, models, api


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"
    _description = "Custom Fields for Fixed Assets Management"

    make_id = fields.Many2one(string="Brand/Make", comodel_name="onehr.fa.fleet.make")
    model_id = fields.Many2one(string="Model", comodel_name="onehr.fa.fleet.model")
    ftc_code = fields.Char(string="Item Code")
    foton_number = fields.Char(string="Unit Number")
    # chassis_number = fields.Char(string="Chassis Number")
    engine_number = fields.Char(string="Engine Number")
    color = fields.Char(string="Color")
    conduction_sticker = fields.Char(string="Conduction Sticker")
    plate_number = fields.Char(string="Plate Number")
    year_model = fields.Integer(string="Year Model")
    seats = fields.Char(string="Seats Number")
    doors = fields.Char(string="Doors Number")
    transmission = fields.Selection(string="Transmission", selection=[("manual", "Manual"), ("automatic", "Automatic")])
    fuel_type = fields.Selection(string="Fuel Type", selection=[
        ("gas", "Gasoline"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid")
    ])
    km_per_liter = fields.Integer(string="KM per liter")
    fa_id = fields.Many2one(string="Fixed Asset", comodel_name="onehr.fixed.assets")
    employee_name = fields.Char(string="Employee", related="fa_id.hr_employee_id.name", readonly=True)
    fa_department_id = fields.Many2one(string="Department", related="fa_id.hr_department_id", readonly=True,
                                       comodel_name="hr.department")
    assigned_to = fields.Char(string="Custodian", related="fa_id.assigned_to")

    @api.onchange('make_id')
    def make_changed(self):
        self.model_id = False
