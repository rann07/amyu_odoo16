from odoo import fields, models, api
from odoo.exceptions import ValidationError

class BcsCollection(models.Model):
    _name = 'bcs.collection'
    _description = "Collection"
    _rec_name = 'name'

    transaction = fields.Char(string="Transaction ID", readonly=1)

    @api.model
    def create(self, vals):
        # name = re.sub(r'\W+', ' ', vals['paid_by_id'])
        # name_array = name.split()
        # if len(name_array) == 1:
        #     transaction = name_array[0][0:3]
        # elif len(name_array) == 2:
        #     name1 = name_array[0]
        #     name2 = name_array[1]
        #     transaction = (name1[0:2] if len(name1) >= 2 else name1[0:1]) + \
        #                   (name2[0:2] if len(name1) == 1 else name2[0:1])
        # elif len(name_array) >= 3:
        #     name1 = name_array[0]
        #     name2 = name_array[1]
        #     name3 = name_array[2]
        #     transaction = name1[0:1] + name2[0:1] + name3[0:1]
        
        # Compute Client ID
        # transaction = self.env['ir.sequence'].next_by_code('collection.id.seq')
        # vals['transaction'] = transaction
        
        res = super(BcsCollection, self).create(vals)
        
        if res:
            # compute transaction id
            res.transaction = f'{res.id:05d}'
            
            # manual posting
            if res.payment_collection == 'consolidated':
                res.unissued_amount_for_ar = res.amount
        
        return res

    name = fields.Char(compute="_compute_name")
    @api.depends("billing_ids", "date_collected", "bank.name", "payment_collection", "paid_by_id", "paid_by_id.name")
    def _compute_name(self):
        for record in self:
            record.name = record.transaction + ' | ' + record.date_collected.strftime("%b %Y") + ' | ' \
                + str(len(record.billing_ids)) + ' Billing' + ('s ' if len(record.billing_ids) > 1 else ' ') \
                + ('(Cash)' if record.payment_mode == 'cash' else f'({record.bank.name})') + ' | ' \
                + (record.paid_by_id.name)
                
    paid_by_id = fields.Many2one(comodel_name='client.profile', string="Paid By (Client)", required=True)

    @api.onchange('paid_by_id')
    def _onchange_paid_by_id(self):
        most_recent_billing = self.env['bcs.billing'].search(
            [('client_id', '=', self.paid_by_id.id)],
            order="transaction desc", limit=1)
        if most_recent_billing:
            self.billing_ids = [(5,)]
            self.billing_ids = [(4, most_recent_billing.id)]
        
        # Check if AR Journal and Billing Summary exists
        if self.paid_by_id:
            arj = self.env['soa.ar.journal'].search([('client_id', '=', self.paid_by_id.id)], limit=1)
            if not arj:
                raise ValidationError('No AR Journal found for this Client.')
            
            bs = self.env['billing.summary'].search([('client_id', '=', self.paid_by_id.id)], limit=1)
            if not bs:
                raise ValidationError('No Billing Summary found for this Client.')
        
    
    recent_billings_per_client = fields.Many2many(comodel_name='bcs.billing', relation='bcs_collection_allowed_billings_rel', 
                                                  compute='_get_recent_billing_per_client')

    @api.depends('paid_by_id')
    def _get_recent_billing_per_client(self):
        # most_recent_billing = self.env['bcs.billing'].search(
        #     [('client_id', '=', self.paid_by_id.id)],
        #     order="transaction desc", limit=1)
        
        bllings = self.env['bcs.billing'].search([('state', '=', 'approved')], order="transaction desc")
        unique_billing_ids = {}
        selected_billings = [b.id for b in self.billing_ids]
        for billing in bllings:
            if billing.id in selected_billings:
                continue
            if billing.client_id.id not in unique_billing_ids.keys():
                unique_billing_ids[billing.client_id.id] = billing
        for record in self:
            # record.recent_billings_per_client = [(6, 0, [value.id for value in bllings])]
            record.recent_billings_per_client = [(6, 0, [value.id for value in unique_billing_ids.values()])]
            
    billing_ids = fields.Many2many(comodel_name='bcs.billing', string="Billing", relation='bcs_collection_selected_billing_rel')
    collection_type = [('direct_payment', 'Direct Payment'),
                       ('consolidated', 'Consolidated Payment'),]
                    #    ('suspense', 'Suspense Account')]
    payment_collection = fields.Selection(collection_type, default='direct_payment', string="Collection Type", required=True)
    allow_edit_billing_ids = fields.Boolean(default=True)
    
    @api.onchange('billing_ids')
    def _onchange_billing_ids(self):
        blen = len(self.billing_ids)
        # if blen == 0:
        #     self.payment_collection = 'suspense'
        if blen == 1:
            self.payment_collection = 'direct_payment'
            self.unissued_amount_for_ar = 0
        elif blen >= 2:
            self.payment_collection = 'consolidated'
        return
    
    collected_by = fields.Many2one(comodel_name='hr.employee',  
                                #   domain=f"[('job_id.name','ilike', 'Liaison')]", 
                                  string="Collected By", required=True)
    date_collected = fields.Date(string="Date Collected", default=fields.Date.today, required=True)
    state_selection = [('draft', 'Draft'),
                       ('submitted', 'Submitted'),
                       ('verified', 'Verified'),
                       ('approved', 'Approved')]
    state = fields.Selection(state_selection, default='draft', copy=False)
    void_collection = fields.Boolean(default=False)
    
    def _validate_billing_statuses(self, next_state):
        for billing in self.billing_ids:
            if billing.status == 'void_billing':
                raise ValidationError(f"Void Billing found ({billing.transaction})."\
                                      +f"This record cannot be {next_state}.")     

    # fad staff edit
    def draft_action(self):
        self.state = 'draft'

    # fad staff manager
    def fad_staff_submitted_action(self):
        next_state = 'submitted'
        self._validate_billing_statuses(next_state=next_state)
        self.state = next_state

    # fad supervisor
    def fad_supervisor_verified_action(self):
        next_state = 'verified'
        self._validate_billing_statuses(next_state=next_state)
        self.state = next_state

    # fad manager
    def fad_manager_approved_action(self):
        next_state = 'approved'
        self._validate_billing_statuses(next_state=next_state)
        self.state = next_state

        # add to ar journal
        if self.payment_collection == 'direct_payment':
            arj = self.env['soa.ar.journal'].search([('client_id', '=', self.paid_by_id.id)], limit=1)
            if arj:
                arj.new_collection(self)
                
            # only one billing since direct payment
            for billing in self.billing_ids:
                upd = self.env['bcs.updates'].search([('billing_id', '=', billing.id)], limit=1)
                if upd:
                    upd.set_confirmed_payment()
                
        # allow_void should now be false in all billings
        for billing in self.billing_ids:
            billing.set_allow_void_false()
            
            
    bank_type = [('bpi', 'BPI'),
                 ('bdo', 'BDO'),
                 ('eastwest', 'EASTWEST'),
                 ('metrobank', 'METROBANK')]
    depository_bank = fields.Selection(bank_type, default='bpi', string="Depository Bank", required=True)
    payment_method = [('check', 'Check'),
                      ('cash', 'Cash'),
                      ('online', 'Online')]
    payment_mode = fields.Selection(payment_method, default='online', string="Mode of Payment", required=True)
    bank = fields.Many2one(comodel_name='bank', string="Bank")
    # If check
    check_number = fields.Char(string="Check Number")
    check_date = fields.Date(string="Check Date")
    # If online
    transaction_generated = fields.Char(string="Transaction Generated")
    transaction_date = fields.Date(string="Transaction Date")
    amount = fields.Float(string="Amount", required=True)
    remarks = fields.Text(string="Remarks")
    unissued_amount_for_ar = fields.Float(string="Unissued Amount For ARs", default=0, readonly=True)
    
    def new_manual_posting(self, payments_collection):
        for billing in self.billing_ids:
            pc_client = payments_collection.ar_journal_id.client_id
            if billing.client_id.id == pc_client.id:
                billing.client_paid()
        self.unissued_amount_for_ar -= payments_collection.amount
        self.allow_edit_billing_ids = False
    
    def manual_posting(self):
        arjs = self.env['soa.ar.journal'].search([('client_id', 'in', [bill.client_id.id for bill in self.billing_ids])])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments Collection',
            'view_mode': 'form',
            'res_model': 'manual.posting',
            'context': {
                'default_collection_id': self.id,
                'default_manual_posting': True,
                # 'readonly_by_pass': False,
                'ar_journal_ids': [a.id for a in arjs],
            },
            'target': 'new',
        }
