from odoo import fields, models


class ServicesType(models.Model):
    _name = 'services.type'
    _description = "Services"
    _rec_name = 'code'
    _sql_constraints = [
        (
            'unique_code',
            'unique(code)',
            'Can\'t have duplicate values.'
        )
    ]

    name = fields.Text(string="Name")
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
    practice = fields.Selection(
        selection=[('assurance_audit', 'Assurance & Audit'), ('tax_services', 'Tax Services'),
                   ('consultancy_services', 'Consultancy Services'), ('strategy_services', 'Strategy Services')],
        string="Practice")

    active = fields.Boolean(string="Active", default=True)
    service_ids = fields.One2many(string="Services", comodel_name='billing.summary', inverse_name="service_ids")
