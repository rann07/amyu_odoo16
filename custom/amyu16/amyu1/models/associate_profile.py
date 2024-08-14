from odoo import fields, models


class AssociateProfile(models.Model):
    _name = 'associate.profile'
    _description = "Associate Profile"
    _rec_name = 'team_id'
    _sql_constraints = [
        (
            'unique_user_id',
            'unique(user_id)',
            'Can\'t have duplicate users.'
        )
    ]

    users_id = fields.Many2one(string="Associate", comodel_name='hr.employee')
    supervisor_id = fields.Many2one(string="Supervisor", comodel_name='res.users')
    manager_id = fields.Many2one(string="Manager", comodel_name='res.users')
    team_id = fields.Many2one(related='users_id.coach_id', string="Team", store=True)
    cluster_id = fields.Many2one(related='users_id.department_id', string="Department")
    job_id = fields.Many2one(string="Job Position", related='users_id.job_id', store=True)
    lead_partner_id = fields.Many2one(string="Partner", comodel_name='res.users')
    image = fields.Image(string="Image")
    client_profile_ids = fields.One2many(string="Clients", comodel_name='client.profile',
                                         inverse_name="team_id")
    user_id = fields.Many2one(string="Name", comodel_name='res.users', default=lambda self: self.env.user)
    director_id = fields.Many2one(string="Director", comodel_name='res.users')
