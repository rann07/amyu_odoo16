from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


# Test
def test_with_logger(data: any = "Debug Message", warn: bool = False) -> None:
    """
        Outputs a debug message in the odoo log file, 5 times in a row
    """
    method = _logger.info if not warn else _logger.warning
    for _ in range(5):
        method(data)


class BillingSummary(models.Model):
    _name = 'billing.summary'
    _description = "Billing Summary"
    _rec_name = 'client_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        (
            'unique_client_id',
            'unique(client_id)',
            'Can\'t have duplicate clients.'
        )
    ]

    client_id = fields.Many2one(string="Client Name", comodel_name='client.profile', required=True, tracking=True)

    image_1012 = fields.Image(string="Image")
    partner_id = fields.Many2one(related='client_id.lead_partner_id', string="Partner")
    manager_id = fields.Many2one(related='client_id.manager_id', string="Manager")
    supervisor_id = fields.Many2one(related='client_id.supervisor_id', string="Supervisor")
    associate_id = fields.Many2one(related='client_id.user_id', string="Associate")
    service_ids = fields.Many2many(comodel_name='services.type', string="Type of Services")
    audit_ids = fields.One2many(comodel_name='audit.billing', inverse_name='billing_summary_id', string="Audit")
    trc_ids = fields.One2many(comodel_name='trc.billing', inverse_name='billing_summary_id', string="TRC")
    books_ids = fields.One2many(comodel_name='books.billing', inverse_name='billing_summary_id', string="Books")
    permit_ids = fields.One2many(comodel_name='business.permit.billing', inverse_name='billing_summary_id',
                                 string="Business Permit")
    gis_ids = fields.One2many(comodel_name='gis.billing', inverse_name='billing_summary_id', string="GIS")
    loa_ids = fields.One2many(comodel_name='loa.billing', inverse_name='billing_summary_id', string="LOA")
    spe_ids = fields.One2many(comodel_name='special.engagement', inverse_name='billing_summary_id',
                              string="Special Engagement")

    has_aud = fields.Boolean(default=False, tracking=True)
    has_trc = fields.Boolean(default=False, tracking=True)
    has_bks = fields.Boolean(default=False, tracking=True)
    has_per = fields.Boolean(default=False, tracking=True)
    has_gis = fields.Boolean(default=False, tracking=True)
    has_loa = fields.Boolean(default=False, tracking=True)
    has_spe = fields.Boolean(default=False, tracking=True)

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
    def ops_manager_verified_action(self):
        self.state = 'verified'

    # fad manager
    def partner_approved_action(self):
        self.state = 'approved'

    def get_services(self):
        services = self.env['billing.summary'].search([('service_ids', '!=', False)])
        return services

    @api.onchange('service_ids')
    def _onchange_services(self):
        service_list = []
        for service in self.service_ids:
            service_list.append(service.code)
        self.has_aud = 'AUD' in service_list
        self.has_trc = 'TRC' in service_list
        self.has_bks = 'BKS' in service_list
        self.has_per = 'PER' in service_list
        self.has_gis = 'GIS' in service_list
        self.has_loa = 'LOA' in service_list
        self.has_spe = 'SPE' in service_list
        return

    def get_services_total_amount(self, included_services_id):
        included = []
        total = 0

        included_code = []
        for service_id in included_services_id:
            included_code.append(service_id.code)

        if 'AUD' in included_code and self.has_aud: included.append(self.audit_ids)
        if 'TRC' in included_code and self.has_trc: included.append(self.trc_ids)
        if 'BKS' in included_code and self.has_bks: included.append(self.books_ids)
        if 'PER' in included_code and self.has_per: included.append(self.permit_ids)
        if 'GIS' in included_code and self.has_gis: included.append(self.gis_ids)
        if 'LOA' in included_code and self.has_loa: included.append(self.loa_ids)
        if 'SPE' in included_code and self.has_spe: included.append(self.spe_ids)

        for services in included:
            for rec in services:
                total += rec.amount
        return total
