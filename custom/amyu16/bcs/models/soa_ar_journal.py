from odoo import fields, models, api


class ARJournal(models.Model):
    _name = 'soa.ar.journal'
    _description = "AR Journal of Client"
    _sql_constraints = [
        (
            'unique_client_id',
            'unique(client_id)',
            'Can\'t have duplicate journal for clients.'
        )
    ]

    client_id = fields.Many2one(string="Client Name", comodel_name='client.profile', required=True)

    # # use this to change value in view
    # view_initial_balance = fields.Float('Initial Balance')

    # # do not show in view
    # initial_balance = fields.Float()
    balance = fields.Float()

    accounts_receivable_ids = fields.One2many(comodel_name='soa.accounts.receivable', inverse_name='ar_journal_id')
    payments_collection_ids = fields.One2many(comodel_name='soa.payments.collection', inverse_name='ar_journal_id')
    ar_ids_count = fields.Integer()
    pc_ids_count = fields.Integer()

    name = fields.Char(string="Name", compute="_compute_name")

    @api.depends("client_id")
    def _compute_name(self):
        for record in self:
            record.name = record.client_id.name

    # @api.onchange('view_initial_balance')
    # def _onchange_initial_balance(self):
    #     self.balance -= self.initial_balance
    #     self.balance += self.view_initial_balance
    #     self.initial_balance = self.view_initial_balance

    def new_billing(self, billing):
        self.balance = billing.amount
        self.ar_ids_count += 1
        ar = self.env['soa.accounts.receivable'].create({
            'ar_journal_id': self.id,
            'billing_id': billing.id,
            'journal_index': self.ar_ids_count
        })
        self.accounts_receivable_ids = [(4, ar.id)]  # this syntax, with 4, means add apparently

    def new_collection(self, collection):
        self.balance -= collection.amount
        self.pc_ids_count += 1
        pc = self.env['soa.payments.collection'].create({
            'ar_journal_id': self.id,
            'collection_id': collection.id,
            'journal_index': self.pc_ids_count
        })
        self.payments_collection_ids = [(4, pc.id)]

    def new_manual_posting(self, payments_collection):
        self.balance -= payments_collection.amount
        self.pc_ids_count += 1
        self.payments_collection_ids = [(4, payments_collection.id)]

    def void_billing(self, billing):
        ar = self.env['soa.accounts.receivable'].search([('billing_id', '=', billing.id)], limit=1)
        if ar:
            self.accounts_receivable_ids = [(2, ar.id)]  # this syntax, with 2, means delete apparently
        self.balance = billing.previous_amount if not len(self.accounts_receivable_ids) == 0 else 0

    def recalculate(self):
        # self.initial_balance = self.view_initial_balance
        # add = sum([ar.amount for ar in self.accounts_receivable_ids], start=self.initial_balance)
        add = self.accounts_receivable_ids[-1].amount if len(self.accounts_receivable_ids) > 0 else 0
        sub = self.payments_collection_ids[-1].amount if len(self.payments_collection_ids) > 0 else 0
        self.balance = add - sub

    """ FOR DEBUGGING PURPOSES ONLY """

    def reset_journal(self):
        self.accounts_receivable_ids = [(6, 0, [])]
        self.payments_collection_ids = [(6, 0, [])]
        self.ar_ids_count = 0
        self.pc_ids_count = 0

    def open_rec(self):
        return {
            'name': 'AR Journal | ' + self.client_id.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'soa.ar.journal',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'form': {'action_buttons': True}}
        }
