from odoo import api, fields, models
from .__constants__ import (
    BILLING_METHOD_CHOICES,
    PAYMENT_METHOD_CHOICES,
    BILLING_METHOD_DEFAULT,
    PAYMENT_METHOD_DEFAULT,
    BANK_TYPE_DEFAULT,
    BANK_TYPES_PER_PAYMENT,
)


class ClientBillingInfo(models.Model):
    _name = 'client.billing.info'
    _description = 'Records of Client preference in Billing'
    _sql_constraints = [
        (
            'unique_name',
            'unique(name)',
            'Can\'t have duplicate values.'
        )
    ]

    name = fields.Char(compute='_compute_name')
    client = fields.Char(string="Client", required=True)
    preferred_billing_method = fields.Selection(BILLING_METHOD_CHOICES, default=BILLING_METHOD_DEFAULT, required=True)
    preferred_payment_method = fields.Selection(PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_DEFAULT, required=True)
    payment_bank_id = fields.Many2one('bank', string="Bank for Payment",
                                      domain=f"[('bank_type', '=', '{BANK_TYPE_DEFAULT}')]")
    remarks = fields.Char()

    # create_uid <- automatic field by odoo16, res.user who created the record
    # create_date <- automatic field by odoo16 to know when was the date the record got created
    # write_uid <- automatic field by odoo16, res.user who updated the record
    # write_date <- automatic field by odoo16 to know when was the last time the record got updated

    @api.depends('client')
    def _compute_name(self):
        for record in self:
            record.name = record.client

    @api.onchange('preferred_payment_method')
    def _onchange_preferred_payment_method(self):
        return {'domain': {'payment_bank_id':
                               [('bank_type', '=', BANK_TYPES_PER_PAYMENT[self.preferred_payment_method])]}}
