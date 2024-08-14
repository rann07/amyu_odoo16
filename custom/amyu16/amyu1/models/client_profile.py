from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError
from datetime import datetime, date


class ClientProfile(models.Model):
    _name = 'client.profile'
    _description = "Profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Client Name", required=True, tracking=True)

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).upper()

    image_101 = fields.Image(string="Image")
    organization_type = fields.Selection(selection=
                                         [('sole_proprietor', 'Sole Proprietor'),
                                          ('general_partnership', 'General Partnership'),
                                          ('general_professional_partnership', 'General Professional Partnership'),
                                          ('domestic_stock', 'Domestic Stock Corporation'),
                                          ('domestic_corp', 'Domestic NSNP Corporation'),
                                          ('foreign_corp', 'Branch of Foreign Corporation'),
                                          ('foreign_nsnp_corp', 'Branch of Foreign NSNP Corporation'),
                                          ('roqh_foreign_corp', 'ROHQ of Foreign Corporation'),
                                          ('representative_office', 'Representative Office')],
                                         string="Organization Type", tracking=True, required=1)
    sole_proprietor_ids = fields.One2many(comodel_name='sole.proprietor', inverse_name='sole_proprietor_id',
                                          string="Sole", tracking=True)
    general_partnership_ids = fields.One2many(comodel_name='general.partnership', inverse_name='general_partnership_id',
                                              string="General", tracking=True)
    general_professional_partnership_ids = fields.One2many(comodel_name='general.professional.partnership',
                                                           inverse_name='general_professional_partnership_id',
                                                           string="General Professional", tracking=True)
    domestic_stock_ids = fields.One2many(comodel_name='domestic.stock', inverse_name='domestic_stock_id',
                                         string="Domestic", tracking=True)
    domestic_corp_ids = fields.One2many(comodel_name='domestic.corp', inverse_name='domestic_corp_id',
                                        string="Domestic NSNP", tracking=True)
    foreign_corp_ids = fields.One2many(comodel_name='foreign.corp', inverse_name='foreign_corp_id',
                                       string="Foreign Corp", tracking=True)
    foreign_nsnp_corp_ids = fields.One2many(comodel_name='foreign.nsnp.corp', inverse_name='foreign_nsnp_corp_id',
                                            string="Foreign NSNP Corp", tracking=True)
    roqh_foreign_corp_ids = fields.One2many(comodel_name='roqh.foreign.corp', inverse_name='roqh_foreign_corp_id',
                                            string="ROQH Foreign Corp", tracking=True)
    representative_office_ids = fields.One2many(comodel_name='representative.office',
                                                inverse_name='representative_office_id',
                                                string="Representative Office", tracking=True)
    industry_class = fields.Selection(selection=
                                      [('agricultural', 'Agricultural Products & Farming Operations'),
                                       ('automotive', 'Automotive & Spare Parts'),
                                       ('', ''), ('utilities', 'Energy, Utilities & Telecommunications'),
                                       ('financial_service', 'Financial Services'),
                                       ('', ''), ('food', 'Food, Beverage & Restaurant Operations'),
                                       ('organization', 'Foundations & Non-Profit Organizations'),
                                       ('appliances', 'Furniture, Appliances & IT Equipment'),
                                       ('construction', 'Hardware & Construction Supplies'),
                                       ('health', 'Healthcare & Pharmaceuticals'),
                                       ('hospital', 'Hospitality & Leisure'),
                                       ('industrial', 'Industrial Manufacturing'),
                                       ('information_technology', 'IT Services & Business Process Outsourcing'),
                                       ('retail', 'Lifestyle & Retail Brands'),
                                       ('entertainment', 'Media & Entertainment'),
                                       ('nothing', 'n.e.c. (not elsewhere classified)'),
                                       ('', ''), ('other_service', 'Other Services'),
                                       ('print_service', 'Printing Services'),
                                       ('consultancy', 'Professional & Consultancy Services'),
                                       ('transport', 'Public Transport Services'),
                                       ('real_estate', 'Real Estate Development & Construction'),
                                       ('stationery', 'Stationery & Paper Products'),
                                       ('logistic', 'Warehousing & Logistics')],
                                      string="Industry Class", tracking=True)
    nature_of_business = fields.Text(string="Nature of Activities, Brands, Product & Services", tracking=True)

    @api.onchange('nature_of_business')
    def caps_nature_of_business(self):
        if self.nature_of_business:
            self.nature_of_business = str(self.nature_of_business).title()
            for record in self:
                if any(text.isdigit() for text in record.nature_of_business):
                    raise ValidationError("Numbers are not allowed in Nature of Activities field.")

    date_of_engagement = fields.Date(string="Engagement Date", required=True, tracking=True)

    @api.onchange('date_of_engagement')
    def _check_future_date(self):
        today = date.today()
        if self.date_of_engagement and self.date_of_engagement > today:
            raise ValidationError("Future dates are not allowed.")

    client_system_generated = fields.Char(string="Client ID", tracking=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('supervisor', 'Supervisor'),
                                        ('manager', 'Manager'),
                                        ('approved', 'Approved'),
                                        ('cancel', 'Returned')], tracking=True, default='draft', string="Status")

    def state_waiting(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    user_id = fields.Many2one(string="Associate", comodel_name='res.users', default=lambda self: self.env.user,
                              tracking=True)
    manager_id = fields.Many2one(string="Manager", related="team_id.manager_id", readonly=True)
    supervisor_id = fields.Many2one(string="Supervisor", related="team_id.supervisor_id", readonly=True)
    cluster_id = fields.Many2one(string="Department", related="team_id.cluster_id", readonly=True)
    lead_partner_id = fields.Many2one(string="Partner", related="team_id.lead_partner_id", readonly=True)
    team_id = fields.Many2one(string="Team", comodel_name='associate.profile', required=1)
    report_period = fields.Selection([('calendar', 'Calendar'), ('fiscal', 'Fiscal')], tracking=True)
    fiscal = fields.Selection(selection=[('3', '3'), ('6', '6'), ('9', '9')], string="Fiscal Month", tracking=True)
    calendar = fields.Selection([('12', '12')], default="12", string="Fiscal Year End", tracking=True)

    def draft_action(self):
        self.state = 'draft'
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    def action_submit_supervisor(self):
        self.state = 'supervisor'

    def action_approve_supervisor(self):
        self.state = 'manager'

    def action_return(self):
        self.state = 'cancel'

    def action_approve_manager(self):
        self.state = 'approved'

    # @api.onchange("name")
    # def compute_name(self):
    #     client_id = ""
    #     if self.date_of_engagement:
    #         name = re.sub(r'\W+', ' ', self.name)
    #         name_array = name.split()
    #         if len(name_array) == 1:
    #             client_id = name_array[0][0:3]
    #         elif len(name_array) == 2:
    #             name1 = name_array[0]
    #             name2 = name_array[1]
    #             print(name1, name2)
    #             client_id = (name1[0:2] if len(name1) >= 2 else name1[0:1]) + \
    #                         (name2[0:2] if len(name1) == 1 else name2[0:1])
    #         elif len(name_array) >= 3:
    #             name1 = name_array[0]
    #             name2 = name_array[1]
    #             name3 = name_array[2]
    #             client_id = name1[0:1] + name2[0:1] + name3[0:1]
    #
    #         print(client_id.upper())

    # def write(self, vals):
    #     if 'name' in vals:
    #         old_id = self.client_system_generated.split("-")[0]
    #         name = re.sub(r'\W+', ' ', vals['name'])
    #         name_array = name.split()
    #
    #         if len(name_array) == 1:
    #             client_system_generated = name_array[0][0:3]
    #         elif len(name_array) == 2:
    #             name1 = name_array[0]
    #             name2 = name_array[1]
    #             client_system_generated = (name1[0:2] if len(name1) >= 2 else name1[0:1]) + \
    #                                       (name2[0:2] if len(name1) == 1 else name2[0:1])
    #         elif len(name_array) >= 3:
    #             name1 = name_array[0]
    #             name2 = name_array[1]
    #             name3 = name_array[2]
    #             client_system_generated = name1[0:1] + name2[0:1] + name3[0:1]
    #         vals.update({'client_system_generated': self.client_system_generated.replace(old_id,
    #                                                                                      client_system_generated).upper()})
    #     super(ClientProfile, self).write(vals)
    #
    # @api.model
    # def create(self, vals):
    #     name = re.sub(r'\W+', ' ', vals['name'])
    #     name_array = name.split()
    #     if len(name_array) == 1:
    #         client_system_generated = name_array[0][0:3]
    #     elif len(name_array) == 2:
    #         name1 = name_array[0]
    #         name2 = name_array[1]
    #         client_system_generated = (name1[0:2] if len(name1) >= 2 else name1[0:1]) + \
    #                                   (name2[0:2] if len(name1) == 1 else name2[0:1])
    #     elif len(name_array) >= 3:
    #         name1 = name_array[0]
    #         name2 = name_array[1]
    #         name3 = name_array[2]
    #         client_system_generated = name1[0:1] + name2[0:1] + name3[0:1]
    #     # Compute Client ID
    #     client_system_generated += "-" + ("0" if int(
    #         datetime.strftime(datetime.strptime(vals['date_of_engagement'], '%Y-%m-%d'), '%Y')) < 2000 else "1") + \
    #                                str(vals['date_of_engagement'])[2:4] + \
    #                                str(vals['date_of_engagement'])[5:7] + "-" + \
    #                                self.env['ir.sequence'].next_by_code('client.id.seq')
    #
    #     vals.update({'client_system_generated': client_system_generated.upper()})
    #     res = super(ClientProfile, self).create(vals)
    #     # if res:
    #     #     self.env['escalation.contact'].create({
    #     #         'level': 'level_1',
    #     #         'timeframe': 'lvl1',
    #     #         'escalation_id': res.id
    #     #     })
    #     #     self.env['escalation.contact'].create({
    #     #         'level': 'level_2',
    #     #         'timeframe': 'lvl2',
    #     #         'escalation_id': res.id
    #     #     })
    #     #     self.env['escalation.contact'].create({
    #     #         'level': 'level_3',
    #     #         'timeframe': 'lvl3',
    #     #         'escalation_id': res.id
    #     #     })
    #     return res
    @api.model
    def create(self, vals):
        res = super(ClientProfile, self).create(vals)

        if res:
            # Add to BCS (AR Journal and Billing Summary)
            self.env['soa.ar.journal'].create({'client_id': res.id, })
            self.env['billing.summary'].create({'client_id': res.id, })

        return res

    registered_unit_no = fields.Char(string="Unit/Floor", tracking=True)

    @api.onchange('registered_unit_no')
    def caps_registered_unit_no(self):
        if self.registered_unit_no:
            self.registered_unit_no = str(self.registered_unit_no).title()

    registered_building_name = fields.Char(string="Building Name", tracking=True)

    @api.onchange('registered_building_name')
    def caps_registered_building_name(self):
        if self.registered_building_name:
            self.registered_building_name = str(self.registered_building_name).title()

    registered_street = fields.Char(string="Street", tracking=True)

    @api.onchange('registered_street')
    def caps_registered_street(self):
        if self.registered_street:
            self.registered_street = str(self.registered_street).title()

    registered_district = fields.Char(string="District/Barangay/Village", tracking=True)

    @api.onchange('registered_district')
    def caps_registered_district(self):
        if self.registered_district:
            self.registered_district = str(self.registered_district).title()

    registered_city = fields.Char(string="City", tracking=True)

    @api.onchange('registered_city')
    def caps_registered_city(self):
        if self.registered_city:
            self.registered_city = str(self.registered_city).title()

    registered_zip = fields.Char(string="Zip Code", size=4, tracking=True)

    @api.constrains('registered_zip')
    def _validate_registered_zip(self):
        for record in self:
            pattern = r'^\d{4}$'  # Modify the regular expression pattern according to your requirements
            if record.registered_zip and not re.match(pattern, record.registered_zip):
                raise ValidationError('Invalid Zip Code!')

    registered_landline = fields.Char(string="Registered Phone", size=9, tracking=True)

    @api.onchange('registered_landline')
    def onchange_registered_landline(self):
        for record in self:
            if record.registered_landline and len(record.registered_landline) == 8:
                formatted_number = '-'.join([
                    record.registered_landline[:4],
                    record.registered_landline[4:8]
                ])
                record.registered_landline = formatted_number

    @api.constrains('registered_landline')
    def _check_registered_landline(self):
        for record in self:
            if record.registered_landline:
                if any(char.isalpha() and char != '-' for char in record.registered_landline):
                    raise ValidationError(
                        "Only numbers are allowed in the Telephone Number.")

    facsimile_no = fields.Char(string="Facsimile", size=9, tracking=True)

    @api.onchange('facsimile_no')
    def onchange_facsimile_no(self):
        for record in self:
            if record.facsimile_no and len(record.facsimile_no) == 8:
                formatted_number = '-'.join([
                    record.facsimile_no[:4],
                    record.facsimile_no[4:8]
                ])
                record.facsimile_no = formatted_number

    @api.constrains('facsimile_no')
    def _check_facsimile_no(self):
        for record in self:
            if record.facsimile_no:
                if any(char.isalpha() and char != '-' for char in record.facsimile_no):
                    raise ValidationError(
                        "Only numbers are allowed in the Facsimile Number.")

    website = fields.Char(string="Website", tracking=True)

    @api.constrains('website')
    def _check_website_format(self):
        for record in self:
            if record.website and '.' not in record.website:
                raise ValidationError("Invalid Website")

    office_admin_unit_no = fields.Char(string="Unit/Floor", tracking=True)

    @api.onchange('office_admin_unit_no')
    def caps_office_admin_unit_no(self):
        if self.office_admin_unit_no:
            self.office_admin_unit_no = str(self.office_admin_unit_no).title()

    office_admin_building_name = fields.Char(string="Building Name", tracking=True)

    @api.onchange('office_admin_building_name')
    def caps_office_admin_building_name(self):
        if self.office_admin_building_name:
            self.office_admin_building_name = str(self.office_admin_building_name).title()

    office_admin_street = fields.Char(string="Street", tracking=True)

    @api.onchange('office_admin_street')
    def caps_office_admin_street(self):
        if self.office_admin_street:
            self.office_admin_street = str(self.office_admin_street).title()

    office_admin_district = fields.Char(string="District/Barangay/Village", tracking=True)

    @api.onchange('office_admin_district')
    def caps_office_admin_district(self):
        if self.office_admin_district:
            self.office_admin_district = str(self.office_admin_district).title()

    office_admin_city = fields.Char(string="City", tracking=True)

    @api.onchange('office_admin_city')
    def caps_office_admin_city(self):
        if self.office_admin_city:
            self.office_admin_city = str(self.office_admin_city).title()

    office_admin_zip = fields.Char(string="Zip Code", size=4, tracking=True)

    @api.constrains('office_admin_zip')
    def _validate_office_admin_zip(self):
        for record in self:
            pattern = r'^\d{4}$'  # Modify the regular expression pattern according to your requirements
            if record.office_admin_zip and not re.match(pattern, record.office_admin_zip):
                raise ValidationError('Invalid Zip Code!')

    primary_contact_landline = fields.Char(string="Telephone", size=9, tracking=True)

    @api.onchange('primary_contact_landline')
    def onchange_primary_contact_landline(self):
        for record in self:
            if record.primary_contact_landline and len(record.primary_contact_landline) == 8:
                formatted_number = '-'.join([
                    record.primary_contact_landline[:4],
                    record.primary_contact_landline[4:8]
                ])
                record.primary_contact_landline = formatted_number

    @api.constrains('primary_contact_landline')
    def _check_primary_contact_landline(self):
        for record in self:
            if record.primary_contact_landline:
                if any(char.isalpha() and char != '-' for char in record.primary_contact_landline):
                    raise ValidationError(
                        "Only numbers are allowed in the Telephone field.")

    primary_contact_person = fields.Char(string="Contact Person", tracking=True)

    @api.onchange('primary_contact_person')
    def caps_primary_contact_person(self):
        if self.primary_contact_person:
            self.primary_contact_person = str(self.primary_contact_person).title()
            for record in self:
                if any(char.isdigit() for char in record.primary_contact_person):
                    raise ValidationError("Numbers are not allowed in Primary Contact Person field.")

    primary_contact_mobile = fields.Char(string="Mobile", size=13, tracking=True)

    @api.constrains('primary_contact_mobile')
    def _validate_primary_contact_mobile(self):
        for record in self:
            pattern = r'^(?:\+63|0)\d{10}$'  # Modify the regular expression pattern according to your requirements
            if record.primary_contact_mobile and not re.match(pattern, record.primary_contact_mobile):
                raise ValidationError('Invalid mobile number format!')

    primary_contact_email = fields.Char(string="Email", tracking=True)

    @api.constrains('primary_contact_email')
    def _check_primary_contact_email_format(self):
        for record in self:
            if record.primary_contact_email and '.' not in record.primary_contact_email:
                raise ValidationError("Invalid email address")

    principal_accounting_officer = fields.Char(string="Principal Accounting Officer", tracking=True)

    @api.onchange('principal_accounting_officer')
    def caps_principal_accounting_officer(self):
        if self.principal_accounting_officer:
            self.principal_accounting_officer = str(self.principal_accounting_officer).title()
            for record in self:
                if any(char.isdigit() for char in record.principal_accounting_officer):
                    raise ValidationError("Numbers are not allowed in Principal Accounting field.")

    principal_accounting_landline = fields.Char(string="Telephone", size=9, tracking=True)

    @api.onchange('principal_accounting_landline')
    def onchange_principal_accounting_landline(self):
        for record in self:
            if record.principal_accounting_landline and len(record.principal_accounting_landline) == 8:
                formatted_number = '-'.join([
                    record.principal_accounting_landline[:4],
                    record.principal_accounting_landline[4:8]
                ])
                record.principal_accounting_landline = formatted_number

    @api.constrains('principal_accounting_landline')
    def _check_principal_accounting_landline(self):
        for record in self:
            if record.principal_accounting_landline:
                if any(char.isalpha() and char != '-' for char in record.principal_accounting_landline):
                    raise ValidationError(
                        "Only numbers are allowed in the Telephone field")

    principal_accounting_mobile = fields.Char(string="Mobile", size=13, tracking=True)

    @api.constrains('principal_accounting_mobile')
    def _validate_principal_accounting_mobile(self):
        for record in self:
            pattern = r'^(?:\+63|0)\d{10}$'  # Modify the regular expression pattern according to your requirements
            if record.principal_accounting_mobile and not re.match(pattern, record.principal_accounting_mobile):
                raise ValidationError('Invalid mobile number format!')

    principal_accounting_email = fields.Char(string="Email", tracking=True)

    @api.constrains('principal_accounting_email')
    def _check_principal_accounting_email_format(self):
        for record in self:
            if record.principal_accounting_email and '.' not in record.principal_accounting_email:
                raise ValidationError("Invalid email address")

    corporate_ids = fields.One2many(comodel_name='corporate.officer', inverse_name='client_profile_id',
                                    string="Corporate Officers", tracking=True)
    vat = fields.Char(string="Tin No", size=11, tracking=True, required=True)

    @api.onchange('vat')
    def onchange_vat(self):
        if self.vat and len(self.vat) == 9:
            formatted_value = '-'.join([self.vat[:3], self.vat[3:6], self.vat[6:]])
            self.vat = formatted_value

    @api.constrains('vat')
    def _check_vat(self):
        for record in self:
            if record.vat:
                if any(char.isalpha() and char != '-' for char in record.vat):
                    raise ValidationError(
                        "Only numbers are allowed in the TAX ID field")

    rdo_code = fields.Char(string="RDO Code", size=4, tracking=True)

    @api.onchange('rdo_code')
    def caps_rdo_code(self):
        if self.rdo_code:
            self.rdo_code = str(self.rdo_code).upper()

    registration_date = fields.Date(string="Registration Date", tracking=True)

    @api.onchange('registration_date')
    def _check_future_registration_date(self):
        today = date.today()
        if self.registration_date and self.registration_date > today:
            raise ValidationError("Future dates are not allowed.")

    income_tax = fields.Boolean(string="Income Tax", tracking=True)
    excise_tax = fields.Boolean(string="Excise Tax", tracking=True)
    value_added_tax = fields.Boolean(string="Value-added Tax", tracking=True)
    withholding_tax_expanded = fields.Boolean(string="Withholding Tax - Expanded", tracking=True)
    withholding_tax_compensation = fields.Boolean(string="Withholding Tax - Compensation", tracking=True)
    withholding_tax_final = fields.Boolean(string="Withholding Tax - Final", tracking=True)
    registration_fee = fields.Boolean(string="Registration Fee", tracking=True)
    other_percentage_tax = fields.Boolean(string="Other Percentage Tax", tracking=True)
    other_percentage_tax_text = fields.Char(tracking=True)
    taxpayer_type = fields.Selection(selection=[
        ('regular', 'Regular'), ('top_5k_individual', 'Top 5k Individual'), (
            'top_20k_corporate', 'Top 20k Corporate'), ('medium_taxpayer', 'Medium Taxpayer'), (
            'large_taxpayer', 'Large Taxpayer'), ('not_applicable', 'N/A')], string="Taxpayer Type",
        tracking=True)
    invoice_tax = fields.Selection(selection=[
        ('bound_padded', 'Bound (Padded)'), ('computer_aid_loose_leaf', 'Computer-aided (Loose-leaf)'), (
            'cas_generated', 'CAS-Generated'), ('not_applicable', 'N/A')], string="Invoice Type",
        tracking=True)
    filing_payment = fields.Selection(
        selection=[('ebir_manual', 'eBIR (Manual)'), ('efps', 'EFPS'), ('not_applicable', 'N/A')],
        string="Filling & Payment", tracking=True)
    books_of_account = fields.Selection(selection=
                                        [('manual', 'Manual'),
                                         ('computer_aid_loose_leaf', 'Computer-aided (Loose-leaf)'),
                                         ('cas_generated', 'CAS-Generated'), ('not_applicable', 'N/A')],
                                        string="Books of Accounts", tracking=True)
    psic_psoc = fields.Char(string="PSIC/PSOC", size=10, tracking=True)

    @api.onchange('psic_psoc')
    def onchange_psic_psoc(self):
        for record in self:
            if record.psic_psoc and len(record.psic_psoc) == 10:
                formatted_number = '-'.join([
                    record.psic_psoc[:4],
                    record.psic_psoc[4:10],
                ])
                record.psic_psoc = formatted_number

    @api.constrains('psic_psoc')
    def _check_psic_psoc(self):
        for record in self:
            if record.psic_psoc:
                if any(char.isalpha() and char != '-' for char in record.psic_psoc):
                    raise ValidationError(
                        "Only numbers are allowed in the PSIC/PSOC field")

    ll_cas_permit_no = fields.Char(string="LL/CAS Permit No", size=15, tracking=True)

    @api.constrains('ll_cas_permit_no')
    def _check_ll_cas_permit_no(self):
        for record in self:
            if record.ll_cas_permit_no:
                if any(char.isalpha() and char != '-' for char in record.ll_cas_permit_no):
                    raise ValidationError(
                        "Only numbers are allowed in the LL/CAS Permit No field")

    pos_crm_spm_yes_no = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], default="no", tracking=True)
    registration_number = fields.Char(string="Registration No", size=13, tracking=True)

    @api.onchange('registration_number')
    def caps_registration_number(self):
        if self.registration_number:
            self.registration_number = str(self.registration_number).upper()

    registration_date_sec = fields.Date("Registration Date", tracking=True)

    @api.onchange('registration_date_sec')
    def _check_future_registration_date_sec(self):
        today = date.today()
        if self.registration_date_sec and self.registration_date_sec > today:
            raise ValidationError("Future dates are not allowed.")

    trade_name = fields.Char(string="Trade Name", tracking=True)

    @api.onchange('trade_name')
    def caps_trade_name(self):
        if self.trade_name:
            self.trade_name = str(self.trade_name).upper()

    date_per_law = fields.Char(string="Date per By-Laws", tracking=True)
    actual_date_meeting = fields.Date('date', tracking=True)
    sec_yes_no = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no", tracking=True)
    company_permit_yes = fields.Text(string="If Yes what type of security is the Company permit to sell?",
                                     tracking=True)
    capitalization_ids = fields.One2many(comodel_name='capitalization.share', inverse_name='capitalization_id',
                                         string="Class of Shares", tracking=True)
    capital_sole_proprietor_ids = fields.One2many(comodel_name='capital.sole.proprietor',
                                                  inverse_name='capital_sole_proprietor_id',
                                                  string="Capital Sole Proprietor", tracking=True)
    capital_general_partner_ids = fields.One2many(comodel_name='capital.general.partnership',
                                                  inverse_name='capital_general_partner_id',
                                                  string="Capital General Partnership", tracking=True)
    capital_general_professional_partner_ids = fields.One2many(comodel_name='capital.general.professional.partnership',
                                                               inverse_name='capital_general_professional_partner_id',
                                                               string="Capital General Partnership", tracking=True)
    capital_domestic_ids = fields.One2many(comodel_name='capital.domestic.nsnp', inverse_name='capital_domestic_id',
                                           string="Capital Domestic NSNP", tracking=True)
    capital_foreign_corp_ids = fields.One2many(comodel_name='capital.foreign.corp',
                                               inverse_name='capital_foreign_corp_id',
                                               string="Capital Foreign Corporation", tracking=True)
    capital_foreign_nsnp_ids = fields.One2many(comodel_name='capital.foreign.nsnp.corp',
                                               inverse_name='capital_foreign_nsnp_id', string="Capital Foreign NSNP",
                                               tracking=True)
    capital_roqh_foreign_corp_ids = fields.One2many(comodel_name='capital.roqh.foreign.corp',
                                                    inverse_name='capital_roqh_foreign_corp_id',
                                                    string="Capital ROQH Foreign", tracking=True)
    capital_representative_office_ids = fields.One2many(comodel_name='capital.representative.office',
                                                        inverse_name='capital_representative_office_id',
                                                        string="Capital Representative Office", tracking=True)
    regulatory_yes_no = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no", tracking=True)
    bangko_sentral_pilipinas = fields.Boolean(string="Bangko Sentral ng Pilipinas", tracking=True)
    bsp_filename = fields.Char(string="Attachment Filename")
    attachment_bsp = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_bsp_rel",
                                      column1="m2m_id", column2="attachment_id", string="Bangko Sentral ng Pilipinas")
    bureau_of_custom = fields.Boolean(string="Bureau of Customs", tracking=True)
    boc_filename = fields.Char(string="Attachment Filename")
    attachment_boc = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_boc_rel",
                                      column1="m2m_id", column2="attachment_id", string="Bureau of Custom")
    professional_regulation_commission = fields.Boolean(string="Professional Regulation Commission", tracking=True)
    prc_filename = fields.Char(string="Attachment Filename")
    attachment_prc = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_prc_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Professional Regulation Commission")
    philippines_council_ngo_certification = fields.Boolean(string="Philippine Council for NGO Certification",
                                                           tracking=True)
    pcnc_filename = fields.Char(string="Attachment Filename")
    attachment_pcnc = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_pcnc_rel",
                                       column1="m2m_id", column2="attachment_id",
                                       string="Philippine Council for NGO Certification")
    cooperative_development_authority = fields.Boolean(string="Cooperative Development Authority", tracking=True)
    cda_filename = fields.Char(string="Attachment Filename")
    attachment_cda = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_cda_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Cooperative Development Authority")
    insurance_commission = fields.Boolean(string="Insurance Commission", tracking=True)
    ic_filename = fields.Char(string="Attachment Filename")
    attachment_ic = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_ic_rel",
                                     column1="m2m_id", column2="attachment_id",
                                     string="Insurance Commission")
    integrated_bar_philippines = fields.Boolean(string="Integrated Bar of the Philippines", tracking=True)
    ibp_filename = fields.Char(string="Attachment Filename")
    attachment_ibp = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_ibp_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Integrated Bar of the Philippines")
    philippines_stock_exchange = fields.Boolean(string="Philippine Stock Exchange", tracking=True)
    pse_filename = fields.Char(string="Attachment Filename")
    attachment_pse = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_pse_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Philippine Stock Exchange")
    construction_industry_authority_philippines = fields.Boolean(
        string="Construction Industry authority of the Philippines (PCAB)", tracking=True)
    ciap_filename = fields.Char(string="Attachment Filename")
    attachment_ciap = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_ciap_rel",
                                       column1="m2m_id", column2="attachment_id",
                                       string="Construction Industry authority of the Philippines (PCAB)")
    philippine_amusement_gaming_corporation = fields.Boolean(string="Philippine Amusement and Gaming Corporation",
                                                             tracking=True)
    pagc_filename = fields.Char(string="Attachment Filename")
    attachment_pagc = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_pagc_rel",
                                       column1="m2m_id", column2="attachment_id",
                                       string="Philippine Amusement and Gaming Corporation")
    land_transportation_franchising_regulatory_board = fields.Boolean(
        string="Land Transportation Franchising and Regulatory Board", tracking=True)
    ltfrb_filename = fields.Char(string="Attachment Filename")
    attachment_ltfrb = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_ltfrb_rel",
                                        column1="m2m_id", column2="attachment_id",
                                        string="Land Transportation Franchising and Regulatory Board")
    regulatory_attachment = fields.Many2many('ir.attachment', string='Attachments')
    attachment_filename = fields.Char(string="Attachment Filename")
    others_regulatory = fields.Boolean(string="Others", tracking=True)
    others_regulatory_text = fields.Char(string="Others", tracking=True)
    sss = fields.Char(string="SSS ER No:", size=15, tracking=True)

    @api.onchange('sss')
    def onchange_sss(self):
        for record in self:
            if record.sss and len(record.sss) == 13:
                formatted_number = '-'.join([
                    record.sss[:2],
                    record.sss[2:10],
                    record.sss[10:]
                ])
                record.sss = formatted_number

    @api.constrains('sss')
    def _check_sss(self):
        for record in self:
            if record.sss:
                if any(char.isalpha() and char != '-' for char in record.sss):
                    raise ValidationError(
                        "Only numbers are allowed in the SSS field.")

    phic = fields.Char(string="PHIC ER No", size=14, tracking=True)

    @api.onchange('phic')
    def onchange_phic(self):
        for record in self:
            if record.phic and len(record.phic) == 12:
                formatted_number = '-'.join([
                    record.phic[:2],
                    record.phic[2:11],
                    record.phic[11:]
                ])
                record.phic = formatted_number

    @api.constrains('phic')
    def _check_phic(self):
        for record in self:
            if record.phic:
                if any(char.isalpha() and char != '-' for char in record.phic):
                    raise ValidationError(
                        "Only numbers are allowed in the PHIC field.")

    hdmf = fields.Char(string="HDMF ER No", size=14, tracking=True)

    @api.onchange('hdmf')
    def onchange_hdmf(self):
        for record in self:
            if record.hdmf and len(record.hdmf) == 12:
                formatted_number = '-'.join([
                    record.hdmf[:4],
                    record.hdmf[4:8],
                    record.hdmf[8:]
                ])
                record.hdmf = formatted_number

    @api.constrains('hdmf')
    def _check_hdmf(self):
        for record in self:
            if record.hdmf:
                if any(char.isalpha() and char != '-' for char in record.hdmf):
                    raise ValidationError(
                        "Only numbers are allowed in the HDMF field.")

    sss_filing = fields.Selection(selection=[('manual', 'Manual'), ('online', 'Online (AMS-CCL)')], string="SSS Filing",
                                  tracking=True)
    phic_filing = fields.Selection(selection=[('manual', 'Manual'), ('online', 'Online (ERPS)')], string="PHIC Filing",
                                   tracking=True)
    hdmf_filing = fields.Selection(selection=[('manual', 'Manual'), ('online', 'Online (eSRS)')], string=" HDMF Filing",
                                   tracking=True)
    sss_pay = fields.Selection(
        selection=[('cash', 'Cash'), ('check', 'Check'), ('online_banking', 'Online Banking (EPS)')],
        string="SSS Payment", tracking=True)
    phic_pay = fields.Selection(
        selection=[('cash', 'Cash'), ('check', 'Check'), ('online_banking', 'Online Banking (EPS)')],
        string="PHIC Payment", tracking=True)
    hdmf_pay = fields.Selection(
        selection=[('cash', 'Cash'), ('check', 'Check'), ('online_banking', 'Online Banking (EPS)')],
        string="HDMF Payment", tracking=True)
    escalation_ids = fields.One2many(comodel_name='escalation.contact', inverse_name='escalation_id',
                                     string="Escalation Point", tracking=True)
    # Tax
    tax_services = fields.Boolean(string="Tax Services", tracking=True)
    tax_report = fields.Boolean(string="Tax Reporting and Filing of Tax Returns", tracking=True)
    tax_investigation = fields.Boolean(string="Tax Investigation Support/Advocate Services", tracking=True)
    tax_review = fields.Boolean(string="Tax Review and Compliance", tracking=True)
    tax_advisory = fields.Boolean(string="Tax Advisory, Opinion and Studies", tracking=True)
    tax_refund = fields.Boolean(string="Application for Tax Refund", tracking=True)
    tax_rule = fields.Boolean(string="Request for Tax Rulings", tracking=True)
    # Assurance
    assurance_services = fields.Boolean(string="Assurance and Audit Services", tracking=True)
    review = fields.Boolean(string="Financial Statement Reviews and Audits", tracking=True)
    extend_audit = fields.Boolean(string="Special/Extended Audits", tracking=True)
    assurance_engagement = fields.Boolean(string="Assurance Engagements on Pro Forma Financial Information",
                                          tracking=True)
    # Advisory
    advisory_services = fields.Boolean(string="Advisory and Consultancy Services", tracking=True)
    business_review = fields.Boolean(string="Business Process Review", tracking=True)
    internal_audit = fields.Boolean(string="Internal Audit and Controls Evaluation", tracking=True)
    risk_management = fields.Boolean(string="Enterprise Risk Management", tracking=True)
    procedures_engagement = fields.Boolean(string="Agreed-upon Procedures Engagements", tracking=True)
    corporate_finance = fields.Boolean(string="Corporate Finance and Financial Planning", tracking=True)
    organizational = fields.Boolean(string="Organizational Structures, Mergers and Acquisition Advisory", tracking=True)
    # Business
    business_services = fields.Boolean(string="Business Support and Process Outsourcing Services", tracking=True)
    accounting = fields.Boolean(string="Accounting Process Outsourcing", tracking=True)
    compilation = fields.Boolean(string="Compilation Engagements", tracking=True)
    accounts_restructuring = fields.Boolean(string="Accounts Restructuring", tracking=True)
    amendment = fields.Boolean(string="Amendment of Articles of Incorporation and By-Laws", tracking=True)
    preparation_gis = fields.Boolean(string="Preparation of General Information Sheet", tracking=True)
    business_registration = fields.Boolean(string="Start-up,Renewal and Closure of Business Registrations",
                                           tracking=True)
    staff_arrangement = fields.Boolean(string="Staffing Augmentation Arrangements", tracking=True)
    # non routinary
    lis = fields.Boolean(string="LIS", tracking=True)
    gis = fields.Boolean(string="GIS", tracking=True)
    inv_list = fields.Boolean(string="Inventory List", tracking=True)
    books_renewal = fields.Boolean(string="Books Renewal", tracking=True)
    business_permit = fields.Boolean(string="Business Permit", tracking=True)

    # documents_count = fields.Integer(compute="action_attach_documents")
    #
    # def action_attach_documents(self):
    #     for rec in self:
    #         rec.documents_count = self.env['client.records'].search_count([
    #             ('client_profile_id', '=', rec.id)
    #         ])
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Working Papers',
    #         'res_model': 'client.records',
    #         'view_mode': 'kanban,form',
    #         'domain': [('client_profile_id', '=', rec.id)],
    #         'context': {'default_client_profile_id': rec.id},
    #         'target': 'current',
    #     }

    # # working papers
    # upload_file = fields.Binary(string='File', attachment=True)
    # file_name = fields.Char(string='Filename')
    # year_field = fields.Date(string="Year")

    # client_ids = fields.One2many(comodel_name='billing.summary', inverse_name='client_id')
    # arjournal_client_ids = fields.One2many(comodel_name='soa.ar.journal', inverse_name='client_id')
