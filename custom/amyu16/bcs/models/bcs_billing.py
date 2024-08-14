from odoo import fields, models, api
from odoo.exceptions import ValidationError


class BcsBilling(models.Model):
    _name = 'bcs.billing'
    _description = "Billing"
    _rec_name = 'name'
    # _rec_name = 'transaction'

    name = fields.Char(compute="_compute_name")
    transaction = fields.Char(string="Transaction ID", readonly="1")
    client_id = fields.Many2one(comodel_name='client.profile', string="Client Name", required=True)

    @api.depends("services_id", "date_billed", "client_id.name")
    def _compute_name(self):
        for record in self:
            services = ''
            if len(record.services_id) > 0:
                for service in record.services_id:
                    services += service.code + ', '
                services = services[:-2]
            else:
                services = 'No Services'
            record.name = str(record.transaction) + ' | ' + record.date_billed.strftime("%b %Y") \
                          + ' | ' + services + ' | ' + record.client_id.name
        return

    @api.model
    def create(self, vals):
        #     name = re.sub(r'\W+', ' ', vals['client_id.name'])
        #     name_array = name.split()
        #     if len(name_array) == 1:
        #         transaction = name_array[0][0:3]
        #     elif len(name_array) == 2:
        #         name1 = name_array[0]
        #         name2 = name_array[1]
        #         transaction = (name1[0:2] if len(name1) >= 2 else name1[0:1]) + \
        #                       (name2[0:2] if len(name1) == 1 else name2[0:1])
        #     elif len(name_array) >= 3:
        #         name1 = name_array[0]
        #         name2 = name_array[1]
        #         name3 = name_array[2]
        #         transaction = name1[0:1] + name2[0:1] + name3[0:1]

        # Compute Client ID
        # transaction += "-" + self.env['ir.sequence'].next_by_code('billing.id.seq')
        res = super(BcsBilling, self).create(vals)
        if res:
            res.transaction = f'{res.id:05d}'
        return res

    @api.onchange('client_id')
    def _onchange_client_id(self):
        if self.client_id:
            arj = self.env['soa.ar.journal'].search([('client_id', '=', self.client_id.id)], limit=1)
            if arj and arj.balance:
                self.previous_amount = arj.balance
            elif not arj:
                raise ValidationError('No AR Journal found for this Client.')

            bs = self.env['billing.summary'].search([('client_id', '=', self.client_id.id)], limit=1)
            if bs:
                self.allowed_service_ids = [(6, 0, [srv.id for srv in bs.service_ids])]
                self.services_id = [(6, 0, [srv.id for srv in bs.service_ids])]
            else:
                raise ValidationError('No Billing Summary found for this Client.')

    @api.model
    def _default_issued_by(self):
        if not self.env.user or not self.env.user.id:
            return False
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    issued_by = fields.Many2one(comodel_name='hr.employee', string="Issued By", default=_default_issued_by)
    date_billed = fields.Date(string="Date Billed", required=True, default=fields.Date.today)
    state_selection = [('draft', 'Draft'),
                       ('submitted', 'Submitted'),
                       ('verified', 'Verified'),
                       ('approved', 'Approved')]
    state = fields.Selection(state_selection, default='draft', copy=False)

    # ops manager create
    def draft_action(self):
        self.state = 'draft'

    # ops manager
    def ops_manager_submitted_action(self):
        self.state = 'submitted'

    # fad supervisor
    def fad_supervisor_verified_action(self):
        self.state = 'verified'

    # fad manager
    def fsd_manager_approved_action(self):
        self.state = 'approved'

        # add to ar journal
        arj = self.env['soa.ar.journal'].search([
            ('client_id', '=', self.client_id.id)], limit=1)
        if arj:
            arj.new_billing(self)

    allow_void = fields.Boolean(default=True)
    status_selection = [('not_sent', 'Not yet sent'),
                        ('sent_to_client', 'Sent to client'),
                        ('client_received', 'Client has received'),
                        ('client_paid', 'Client has paid'),
                        ('void_billing', 'Void Statement')]
    status = fields.Selection(status_selection, default='not_sent')

    # only appear when status == 'sent_to_client'
    sent_with_email = fields.Boolean(default=True, string="Sent with Email")
    sent_with_errand = fields.Boolean(string="Sent with Errand")

    # fad has sent billing to client
    def sent_to_client(self):
        self.status = 'sent_to_client'

        # add to for-updates collection
        self.env['bcs.updates'].create({'billing_id': self.id})

    # client confirms they received it
    def client_received(self):
        self.status = 'client_received'

    # client has paid the billing
    def client_paid(self):
        # '''
        # This function is only called by bcs_collection.py.
        # Even if not complete, as long as collection exists, the client has "paid" the billing.
        # This is the basis of the Collection Report (?)
        # '''
        self.status = 'client_paid'

    # billing is apparently void
    def void_billing(self):
        if not self.allow_void:
            return

        self.status = 'void_billing'

        # CONSTRAINT: check first if the most recent billing, is the same as this record
        # past billings can no longer be voided
        most_recent_billing = self.env['bcs.billing'].search(
            [('state', '=', 'approved'), ('client_id', '=', self.client_id.id)],
            order="transaction desc", limit=1)
        if most_recent_billing.id != self.id:
            self.allow_void = False
            return

        # update ar journal
        arj = self.env['soa.ar.journal'].search([('client_id', '=', self.client_id.id)], limit=1)
        if arj:
            arj.void_billing(self)

    def set_allow_void_false(self):
        self.allow_void = False

    # @api.constrains('state')
    # def _check_state_for_editing(self):
    #     for record in self:
    #         if record.state == 'approved' and any(
    #                 record[field] != record._origin[field] for field in ['status', 'billing_sent']):
    #             raise ValidationError("Fields can only be edited when state is not 'approved'.")

    other = fields.Text(string="Other Instruction")
    services_id = fields.Many2many(comodel_name="services.type", string="Services", required=True,
                                   relation="bcs_billing_selected_services_rel")
    allowed_service_ids = fields.Many2many(comodel_name="services.type", string="Allowed Services",
                                           relation="bcs_billing_allowed_services_rel")

    billing_service_ids = fields.Many2many('billing.service')

    @api.onchange('services_id')
    def _onchange_services_id(self):
        self._calculate_amount_services(onchange=True)

    previous_amount = fields.Float(string="Previous Amount")
    services_amount = fields.Float(string="Services Amount")
    amount = fields.Float(string="Total Amount", compute="_compute_amount")
    remarks = fields.Text(string="Remarks")

    @api.depends('previous_amount', 'services_amount')
    def _compute_amount(self):
        for record in self:
            record.amount = record.previous_amount + record.services_amount

    @api.onchange('services_id')
    def _onchange_services_id(self):
        # '''
        # Need for displaying amounts for Billing Summary of client in Billing
        # '''
        bs = self.env['billing.summary'].search([('client_id', '=', self.client_id.id)], limit=1)
        if bs:
            self.services_amount = bs.get_services_total_amount(self.services_id)
            # services_amount_tuples = bs.get_services_each_amount(self.services_id)
            # billing_service_ids = []
            # for service_tuple in services_amount_tuples:

            #     billing_service_ids.append(self.env['bcs.billing.service'].create({
            #         'service_view': service_tuple[0],
            #         'amount': service_tuple[1],
            #     }))
            # self.billing_service_ids = [(5,), (6, 0, [bs.id for bs in billing_service_ids])]
