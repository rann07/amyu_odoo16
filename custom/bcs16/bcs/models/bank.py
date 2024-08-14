from odoo import api, fields, models


class Bank(models.Model):
    _name = 'bank'
    _description = 'Bank records'
    _sql_constraints = [
        (
            'unique_name',
            'unique(name)',
            'Can\'t have duplicate values.'
        )
    ]

    name = fields.Char(string="Name", required=True)
    bank_type = fields.Selection([('online', 'Online'), ('physical', 'Physical')], default='online', required=True)
    address = fields.Char(string="Address")
    remarks = fields.Char(string="Remarks")
