from odoo import models, fields, api
from datetime import datetime


class BillingCollection(models.Model):
    _name = 'billing.collection'
    _rec_name = 'billing_id'

    billing_id = fields.Many2one(comodel_name='bcs.billing', string="Client Name", required=True)
    first_followup = fields.Boolean(string='1st Follow-up')
    second_followup = fields.Boolean(string='2nd Follow-up')
    responded = fields.Boolean(string='Responded')
    confirmed_payment = fields.Boolean(string='Confirmed Payment')

    date_first_followup = fields.Datetime(string='Date')
    date_second_followup = fields.Datetime(string='Date')
    date_responded = fields.Datetime(string='Date Responded')
    date_confirmed_payment = fields.Datetime(string='Date Confirmed Payment')
    last_updated = fields.Datetime(string='Last Updated')

    @api.onchange('first_followup')
    def _onchange_first_followup(self):
        if not self.first_followup:
            self.date_first_followup = False
        else:
            self.date_first_followup = datetime.now()

    @api.onchange('second_followup')
    def _onchange_second_followup(self):
        if not self.second_followup:
            self.date_second_followup = False
        else:
            self.date_second_followup = datetime.now()

    @api.onchange('responded')
    def _onchange_responded(self):
        if not self.responded:
            self.date_responded = False
        else:
            self.date_responded = datetime.now()

    @api.onchange('confirmed_payment')
    def _onchange_confirmed_payment(self):
        if not self.confirmed_payment:
            self.date_confirmed_payment = False
        else:
            self.date_confirmed_payment = datetime.now()
            self.billing_id.status = 'client_received'

    @api.model
    def create(self, vals):
        vals['last_updated'] = fields.Datetime.now()
        return super(BillingCollection, self).create(vals)

    def write(self, vals):
        if vals:
            vals['last_updated'] = fields.Datetime.now()
        return super(BillingCollection, self).write(vals)
