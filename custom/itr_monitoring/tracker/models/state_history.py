from odoo import models, fields


class StateHistory(models.Model):
    _name = 'state.history'
    _description = 'State History'

    object_id = fields.Many2one(comodel_name='task.view', string='Object')
    state = fields.Selection(related='object_id.state', string='State')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    user_id = fields.Many2one(comodel_name='res.users', string='User', default=lambda self: self.env.user)
