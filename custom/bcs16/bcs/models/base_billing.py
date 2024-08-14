from odoo import fields, models, api


class BaseBilling(models.Model):
    _name = 'base.billing'

    billing_summary_id = fields.Many2one('billing.summary', string='Billing Summary')
    service_fee = fields.Float(default=0)
    ope_rate = fields.Float(default=0)
    ope = fields.Float(compute='_compute_ope', store=True)
    vat = fields.Float(default=0.12)
    amount = fields.Float(compute='_compute_amount', store=True)
    remarks = fields.Text()

    @api.depends('service_fee', 'ope_rate')
    def _compute_ope(self):
        for record in self:
            record.ope = record.service_fee * record.ope_rate

    @api.depends('service_fee', 'ope', 'vat')
    def _compute_amount(self):
        for record in self:
            record.amount = record.service_fee + record.ope + ((record.service_fee + record.ope) * record.vat)


class AuditBilling(models.Model):
    _name = 'audit.billing'
    _inherit = 'base.billing'
    _description = "Audit Billing"

    billing_month = fields.Selection([('0', 'January'),
                                      ('1', 'February'),
                                      ('2', 'March'),
                                      ('3', 'April'),
                                      ('4', 'May'),
                                      ('5', 'June'),
                                      ('6', 'July'),
                                      ('7', 'August'),
                                      ('8', 'September'),
                                      ('9', 'October'),
                                      ('10', 'November'),
                                      ('11', 'December')
                                      ], string='Billing Month')
    payment_term = fields.Float(string="Payment Term", default=1)
    details = fields.Text(string="Details of Service Engagement")
    billing_summary_id = fields.Many2one(comodel_name='billing.summary', string="Billing Summary")


class TRCBilling(models.Model):
    _name = 'trc.billing'
    _inherit = 'base.billing'
    _description = "TRC Billing"

    name = fields.Date(string="Taxable Reporting Period Start Date")
    end_date = fields.Date(string="Taxable Reporting Period End Date")
    tax_report_period = fields.Date(string="Tax Reporting Period")
    payment_term = fields.Float(string="Payment Terms", default=1)
    details = fields.Text(string="Details of Service Engagement")
    billing_summary_id = fields.Many2one(string="Billing Summary", comodel_name='billing.summary')


class BooksBilling(models.Model):
    _name = 'books.billing'
    _inherit = 'base.billing'
    _description = "Books Billing"

    billing_month = fields.Selection([('0', 'January'),
                                      ('1', 'February'),
                                      ('2', 'March'),
                                      ('3', 'April'),
                                      ('4', 'May'),
                                      ('5', 'June'),
                                      ('6', 'July'),
                                      ('7', 'August'),
                                      ('8', 'September'),
                                      ('9', 'October'),
                                      ('10', 'November'),
                                      ('11', 'December')
                                      ], string='Billing Month')
    period_covered = fields.Date(string="Period Covered")
    branches = fields.Integer(string="No. of Offices or Branches")
    payment_term = fields.Float(string="Payment Terms", default=1)
    reimbursible = fields.Float(string="Reimbursible")
    billing_summary_id = fields.Many2one(comodel_name='billing.summary', string="Billing Summary")


class BusinessPermitsBilling(models.Model):
    _name = 'business.permit.billing'
    _inherit = 'base.billing'
    _description = "Business Permit Billing"

    billing_month = fields.Selection([('0', 'January'),
                                      ('1', 'February'),
                                      ('2', 'March'),
                                      ('3', 'April'),
                                      ('4', 'May'),
                                      ('5', 'June'),
                                      ('6', 'July'),
                                      ('7', 'August'),
                                      ('8', 'September'),
                                      ('9', 'October'),
                                      ('10', 'November'),
                                      ('11', 'December')
                                      ], string='Billing Month')
    period_covered = fields.Date(string="Period Covered")
    branches = fields.Integer(string="No. of Offices or Branches")
    reimbursible = fields.Float(string="Reimbursible")
    billing_summary_id = fields.Many2one(comodel_name='billing.summary', string="Billing Summary")


class GisBilling(models.Model):
    _name = 'gis.billing'
    _inherit = 'base.billing'
    _description = "GIS Billing"

    billing_month = fields.Selection([('0', 'January'),
                                      ('1', 'February'),
                                      ('2', 'March'),
                                      ('3', 'April'),
                                      ('4', 'May'),
                                      ('5', 'June'),
                                      ('6', 'July'),
                                      ('7', 'August'),
                                      ('8', 'September'),
                                      ('9', 'October'),
                                      ('10', 'November'),
                                      ('11', 'December')
                                      ], string='Billing Month')
    details = fields.Text(string="Details of Service Engagement")
    billing_summary_id = fields.Many2one(comodel_name='billing.summary', string="Billing Summary")


class LoaBilling(models.Model):
    _name = 'loa.billing'
    _inherit = 'base.billing'
    _description = "LOA Billing"

    name = fields.Date(string="Billing Request Date")
    payment_term = fields.Float(string="Payment Terms", default=1)
    letter_date = fields.Date(string="Letter Date")
    period_covered = fields.Date(string="Period Covered")
    details = fields.Text(string="Details of Service Engagement")
    billing_summary_id = fields.Many2one(comodel_name='billing.summary', string="Billing Summary")


class SpecialEngagement(models.Model):
    _name = 'special.engagement'
    _inherit = 'base.billing'
    _description = 'Special Engagement'

    billing_month = fields.Selection([('0', 'January'),
                                      ('1', 'February'),
                                      ('2', 'March'),
                                      ('3', 'April'),
                                      ('4', 'May'),
                                      ('5', 'June'),
                                      ('6', 'July'),
                                      ('7', 'August'),
                                      ('8', 'September'),
                                      ('9', 'October'),
                                      ('10', 'November'),
                                      ('11', 'December')
                                      ], string='Billing Month')
    payment_terms = fields.Float(string='Payment Terms', default=1)
    service_id = fields.Many2one('services.type', string='Type of Engagement')
    service_details = fields.Text(string='Details of Service Engagement')
    billing_summary_id = fields.Many2one(comodel_name='billing.summary', string="Billing Summary")
