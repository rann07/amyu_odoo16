from odoo import models, fields


class TeamGroup(models.Model):
    _name = 'team.group'
    _description = "Team"
    _rec_name = 'team_id'

    team_id = fields.Many2one(string="Team", comodel_name='associate.team')
    supervisor_id = fields.Many2one(string="Supervisor", comodel_name='res.users')
    manager_id = fields.Many2one(string="Manager", comodel_name='res.users')
    partners_id = fields.Many2one(string="Partner", comodel_name='res.users')


class AssociateTeam(models.Model):
    _name = 'associate.team'
    _description = "Group Team"

    name = fields.Char(string="Group Name")
