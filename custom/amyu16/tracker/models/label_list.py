from odoo import models, fields


class LabelList(models.Model):
    _name = 'label.list'
    _description = "Label Selection"

    name = fields.Selection(string="Label",
                            selection=[('checked', 'Checked'), ('review', 'Review'), ('approved', 'Approved'),
                                       ('proofread', 'Proofread')])
    active = fields.Boolean(string="Active")
    label_id = fields.Many2one(string="Label", comodel_name='task.view')


class StateLabel(models.Model):
    _name = 'state.label'
    _description = "State Label"
    STATES = [('draft', 'Client List'), ('preparation', 'Preparation'), ('checking', 'Checking'), ('review', 'Review'),
              ('initial_approval', 'Init. Approval'), ('proofread', 'Proofread'),
              ('final_checking', 'FNL Checking'), ('final_review', 'FNL Review'),
              ('final_approval', 'FNL Approval'), ('final_proofread', 'FNL Proofread'),
              ('iar_review', 'IAR Review'), ('printing', 'Printing'), ('sorting', 'Sorting'),
              ('qcc', 'Quality Control Check'), ('filing', 'Filing'), ('filed', 'Filed')]

    name = fields.Selection(STATES, string="State")
    state_id = fields.Many2one(string="Label", comodel_name='task.view')
