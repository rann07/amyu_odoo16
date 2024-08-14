from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CapitalDomesticNsnp(models.Model):
    _name = 'capital.domestic.nsnp'
    _description = "Capital Domestic NSNP"

    name = fields.Float(string="Capital Contribution Amount")
    capital_domestic_id = fields.Many2one(comodel_name='client.profile',
                                          string="Capital Contribution Amount")


class CapitalForeignCorp(models.Model):
    _name = 'capital.foreign.corp'
    _description = "Capital Foreign Corporation"

    name = fields.Float(string="Assigned Capital Amount")
    capital_foreign_corp_id = fields.Many2one(comodel_name='client.profile',
                                              string="Assigned Capital Amount")


class CapitalForeignNsnp(models.Model):
    _name = 'capital.foreign.nsnp.corp'
    _description = "Capital Foreign NSNP"

    name = fields.Float(string="Assigned Capital Amount")
    capital_foreign_nsnp_id = fields.Many2one(comodel_name='client.profile',
                                              string="Assigned Capital Amount")


class CapitalGeneralPartnership(models.Model):
    _name = 'capital.general.partnership'
    _description = "Capital General Partnership"

    name = fields.Char(string="Partner")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in Partner Field.")

    capital_contribution_amount = fields.Float(string="Capital Contribution Amount")
    capital_general_partner_id = fields.Many2one(comodel_name='client.profile',
                                                 string="Capital Contribution Amount")


class CapitalGeneralProfessionalPartnership(models.Model):
    _name = 'capital.general.professional.partnership'
    _description = "Capital General Partnership"

    name = fields.Char(string="Partner")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in Partner Field.")

    capital_contribution_amount = fields.Float(string="Capital Contribution Amount")
    capital_general_professional_partner_id = fields.Many2one(comodel_name='client.profile',
                                                              string="Capital Contribution Amount")


class CapitalRepresentativeOffice(models.Model):
    _name = 'capital.representative.office'
    _description = "Capital Representative Office"

    name = fields.Float(string="Assigned Capital Amount")
    capital_representative_office_id = fields.Many2one(comodel_name='client.profile',
                                                       string="Assigned Capital Amount")


class CapitalRoqhForeignCorp(models.Model):
    _name = 'capital.roqh.foreign.corp'
    _description = "Capital ROQH Foreign Corporation"

    name = fields.Float(string="Assigned Capital Amount")
    capital_roqh_foreign_corp_id = fields.Many2one(comodel_name='client.profile',
                                                   string="Assigned Capital Amount")


class CapitalSoleProprietor(models.Model):
    _name = 'capital.sole.proprietor'
    _description = "Capital Sole Proprietor"

    name = fields.Float(string="Capital Contribution Amount")
    capital_sole_proprietor_id = fields.Many2one(comodel_name='client.profile',
                                                 string="Capital Contribution Amount")


class CapitalizationShare(models.Model):
    _name = 'capitalization.share'
    _description = "Capitalization Shares"

    name = fields.Char(string="Class of Shares")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in Class of Share Field.")

    par_value = fields.Integer(string="Par Value per Share")
    # column_3 = fields.Char(string="Authorized")
    authorized_no = fields.Integer(string=" Authorized No.")
    authorized_amount = fields.Float(string="Amount")
    # column_4 = fields.Char(string="Subscribed")
    subscribed_no = fields.Integer(string="Subscribed No.")
    subscribed_amount = fields.Float(string="Amount")
    # column_5 = fields.Char(string="Treasury")
    treasury_no = fields.Integer(string="Treasury No.")
    treasury_amount = fields.Float(string="Amount")
    # column_6 = fields.Char(string="Paid-Up")
    paid_up_no = fields.Integer(string="Paid-Up No.")
    paid_up_amount = fields.Float(string="Amount")
    capitalization_id = fields.Many2one(comodel_name='client.profile', string="Class")
