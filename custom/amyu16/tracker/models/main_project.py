from odoo import models, fields, api


class MainProject(models.Model):
    _name = 'main.project'
    _description = "Main View FSMS"

    name = fields.Many2one(comodel_name='team.group', string="Group")

    def action_view_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Status',
            'view_mode': 'kanban',
            'res_model': 'task.view',
            'context': {'default_project_id': self.id},
        }
