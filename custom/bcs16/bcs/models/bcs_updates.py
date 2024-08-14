from odoo import models, fields, api
from datetime import datetime
import pytz


class ForCollectionUpdates(models.Model):
    _name = 'bcs.updates'
    _description = "Collections Update"
    _rec_name = 'billing_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    billing_id = fields.Many2one(comodel_name='bcs.billing', string="Billing Transaction", required=True, readonly=True)
    first_followup = fields.Boolean(string='1st Follow-up', tracking=True)
    second_followup = fields.Boolean(string='2nd Follow-up', tracking=True)
    third_followup = fields.Boolean(string='3rd Follow-up', tracking=True)
    # responded = fields.Boolean(string='Responded')
    confirmed_payment = fields.Boolean(string='Confirmed Payment', tracking=True)

    date_first_followup = fields.Datetime(string='Date')
    date_second_followup = fields.Datetime(string='Date')
    date_third_followup = fields.Datetime(string='Date')
    # date_responded = fields.Datetime(string='Date Responded')
    date_confirmed_payment = fields.Datetime(string='Date Confirmed')

    remarks = fields.Text(tracking=True)
    second_remarks = fields.Text(tracking=True)
    third_remarks = fields.Text(tracking=True)

    # used for view; formatted display
    view_first_followup = fields.Char(string="1st Follow-up", tracking=True)
    view_second_followup = fields.Char(string="2nd Follow-up", tracking=True)
    view_third_followup = fields.Char(string="3rd Follow-up", tracking=True)
    # view_responded = fields.Char(string='Responded', compute='_compute_responded')
    view_confirmed = fields.Char(string='Confirmed Payment', tracking=True)

    # @api.depends('first_followup')
    # def _compute_first_followup(self):
    #     for record in self:
    #         record.date_first_followup, record.view_first_followup = self._update_datetime(record.first_followup)
    #         # record.date_first_followup = {'readonly': record.first_followup}
    #
    # @api.depends('second_followup')
    # def _compute_second_followup(self):
    #     for record in self:
    #         record.date_second_followup, record.view_second_followup = self._update_datetime(record.second_followup)
    #
    # @api.depends('third_followup')
    # def _compute_third_followup(self):
    #     for record in self:
    #         record.date_third_followup, record.view_third_followup = self._update_datetime(record.third_followup)
    #
    # @api.depends('confirmed_payment')
    # def _compute_confirmed_payment(self):
    #     for record in self:
    #         record.date_confirmed_payment, record.view_confirmed = self._update_datetime(record.confirmed_payment)
    #         self.billing_id.status = 'client_received' if self.confirmed_payment else 'sent_to_client'
    #
    # def _update_datetime(self, now):
    #     if not now:
    #         return False, ''
    #     dt = datetime.now()
    #     return dt, f'{dt.astimezone(pytz.timezone("Asia/Manila")).strftime("%b. %d, %Y | %I:%M %p")}'

    @api.model
    def create(self, vals):
        if vals.get('first_followup'):
            now_local = datetime.now()
            now_utc = pytz.utc.localize(now_local)
            manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
            vals['view_first_followup'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
        else:
            if vals.get('second_followup'):
                now_local = datetime.now()
                now_utc = pytz.utc.localize(now_local)
                manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
                vals['view_second_followup'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
            else:
                if vals.get('third_followup'):
                    now_local = datetime.now()
                    now_utc = pytz.utc.localize(now_local)
                    manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
                    vals['view_third_followup'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
                else:
                    if vals.get('confirmed_payment'):
                        now_local = datetime.now()
                        now_utc = pytz.utc.localize(now_local)
                        manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
                        vals['view_confirmed'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
                        self.billing_id.status = 'client_received' if self.confirmed_payment else 'sent_to_client'
        return super(ForCollectionUpdates, self).create(vals)

    def write(self, vals):
        if vals.get('first_followup'):
            now_local = datetime.now()
            now_utc = pytz.utc.localize(now_local)
            manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
            vals['view_first_followup'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
        else:
            if vals.get('second_followup'):
                now_local = datetime.now()
                now_utc = pytz.utc.localize(now_local)
                manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
                vals['view_second_followup'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
            else:
                if vals.get('third_followup'):
                    now_local = datetime.now()
                    now_utc = pytz.utc.localize(now_local)
                    manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
                    vals['view_third_followup'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
                else:
                    if vals.get('confirmed_payment'):
                        now_local = datetime.now()
                        now_utc = pytz.utc.localize(now_local)
                        manila_time = now_utc.astimezone(pytz.timezone("Asia/Manila"))
                        vals['view_confirmed'] = manila_time.strftime("%b. %d, %Y | %I:%M %p")
                        self.billing_id.status = 'client_received' if self.confirmed_payment else 'sent_to_client'
        return super(ForCollectionUpdates, self).write(vals)
