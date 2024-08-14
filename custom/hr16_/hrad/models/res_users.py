from odoo import fields, models


class ResUser(models.Model):
    _inherit = 'res.users'

    device_ids = fields.One2many(string="Devices", comodel_name='res.users.devices', inverse_name='user_id')
    guard = fields.Boolean(string="Guard", default=False)


class ResUserDevices(models.Model):
    _name = 'res.users.devices'
    _description = 'User Devices'

    name = fields.Char(string="Token")
    user_id = fields.Many2one(string="User", comodel_name='res.users')
