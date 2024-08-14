from odoo import models, fields


class GroupPartner(models.Model):
    _name = 'group.cluster'
    _description = "Maintenance for Partner Selection"

    name = fields.Char(string="Name")
    cluster_ids = fields.One2many(string="Name", comodel_name='main.view', inverse_name="cluster_id")


class GroupManager(models.Model):
    _name = 'team.manager'
    _description = "Maintenance for manager Selection"

    name = fields.Char(string="Name")
    managers_ids = fields.One2many(string="Name", comodel_name='main.view', inverse_name="managers_id")


class GroupSupervisor(models.Model):
    _name = 'team.supervisor'
    _description = "Maintenance for manager Selection"

    name = fields.Char(string="Name")
    supervisors_ids = fields.One2many(string="Name", comodel_name='main.view', inverse_name="supervisors_id")



