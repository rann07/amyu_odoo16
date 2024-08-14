from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CorporateOfficer(models.Model):
    _name = "corporate.officer"
    _description = "Corporate Officers"

    name = fields.Char(string='Name', required=True)
    client_profile_id = fields.Many2one(comodel_name='client.profile', string="Corporate")


class DomesticCorp(models.Model):
    _name = 'domestic.corp'
    _description = "Domestic NSNP Corp"

    name = fields.Char(string="Chairman of the BOT")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in Chairman of the BOT Field.")

    president = fields.Char(string="President/CEO")

    @api.onchange('president')
    def caps_president(self):
        if self.president:
            self.president = str(self.president).title()
            for record in self:
                if any(char.isdigit() for char in record.president):
                    raise ValidationError("Numbers are not allowed in President/CEO Field.")

    treasurer = fields.Char(string="Treasurer/CFO")

    @api.onchange('treasurer')
    def caps_treasurer(self):
        if self.treasurer:
            self.treasurer = str(self.treasurer).title()
            for record in self:
                if any(char.isdigit() for char in record.treasurer):
                    raise ValidationError("Numbers are not allowed in Treasurer/CFO Field.")

    corporate_secretary = fields.Char(string="Corporate Secretary")

    @api.onchange('corporate_secretary')
    def caps_corporate_secretary(self):
        if self.corporate_secretary:
            self.corporate_secretary = str(self.corporate_secretary).title()
            for record in self:
                if any(char.isdigit() for char in record.corporate_secretary):
                    raise ValidationError("Numbers are not allowed in Corporate Secretary Field.")

    vice_chairman = fields.Char(string="Vice-Chairman of the BOT")

    @api.onchange('vice_chairman')
    def caps_vice_chairman(self):
        if self.vice_chairman:
            self.vice_chairman = str(self.vice_chairman).title()
            for record in self:
                if any(char.isdigit() for char in record.vice_chairman):
                    raise ValidationError("Numbers are not allowed in Vice-Chairman of the BOT Field.")

    asst_treasurer = fields.Char(string="Asst.Treasurer")

    @api.onchange('asst_treasurer')
    def caps_asst_treasurer(self):
        if self.asst_treasurer:
            self.asst_treasurer = str(self.asst_treasurer).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_treasurer):
                    raise ValidationError("Numbers are not allowed in Asst.Treasurer Field.")

    asst_corp_secretary = fields.Char(string="Asst.Corporate Secretary")

    @api.onchange('asst_corp_secretary')
    def caps_asst_corp_secretary(self):
        if self.asst_corp_secretary:
            self.asst_corp_secretary = str(self.asst_corp_secretary).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_corp_secretary):
                    raise ValidationError("Numbers are not allowed in Asst.Corporate Secretary Field.")

    domestic_corp_id = fields.Many2one(comodel_name='client.profile', string="Domestic NSNP Corporation")


class DomesticStock(models.Model):
    _name = 'domestic.stock'
    _description = "Domestic Stock"

    name = fields.Char(string="Chairman of the BOD")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in Chairman of the BOD Field.")

    president = fields.Char(string="President/CEO")

    @api.onchange('president')
    def caps_president(self):
        if self.president:
            self.president = str(self.president).title()
            for record in self:
                if any(char.isdigit() for char in record.president):
                    raise ValidationError("Numbers are not allowed in President/CEO Field.")

    treasurer = fields.Char(string="Treasurer/CFO")

    @api.onchange('treasurer')
    def caps_treasurer(self):
        if self.treasurer:
            self.treasurer = str(self.treasurer).title()
            for record in self:
                if any(char.isdigit() for char in record.treasurer):
                    raise ValidationError("Numbers are not allowed in Treasurer/CFO Field.")

    corporate_secretary = fields.Char(string="Corporate Secretary")

    @api.onchange('corporate_secretary')
    def caps_corporate_secretary(self):
        if self.corporate_secretary:
            self.corporate_secretary = str(self.corporate_secretary).title()
            for record in self:
                if any(char.isdigit() for char in record.corporate_secretary):
                    raise ValidationError("Numbers are not allowed in Corporate Secretary Field.")

    vice_chairman = fields.Char(string="Vice-Chairman of the BOD")

    @api.onchange('vice_chairman')
    def caps_vice_chairman(self):
        if self.vice_chairman:
            self.vice_chairman = str(self.vice_chairman).title()
            for record in self:
                if any(char.isdigit() for char in record.vice_chairman):
                    raise ValidationError("Numbers are not allowed in Vice-Chairman of the BOD Field.")

    asst_treasurer = fields.Char(string="Asst.Treasurer")

    @api.onchange('asst_treasurer')
    def caps_asst_treasurer(self):
        if self.asst_treasurer:
            self.asst_treasurer = str(self.asst_treasurer).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_treasurer):
                    raise ValidationError("Numbers are not allowed in Asst.Treasurer Field.")

    asst_corp_secretary = fields.Char(string="Asst.Corporate Secretary")

    @api.onchange('asst_corp_secretary')
    def caps_asst_corp_secretary(self):
        if self.asst_corp_secretary:
            self.asst_corp_secretary = str(self.asst_corp_secretary).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_corp_secretary):
                    raise ValidationError("Numbers are not allowed in Asst.Corporate Secretary Field.")

    domestic_stock_id = fields.Many2one(comodel_name='client.profile', string="Domestic Stock")


class ForeignNsnpCorp(models.Model):
    _name = 'foreign.nsnp.corp'
    _description = "Branch of Foreign NSNP Corp"

    name = fields.Char(string="Country Manager")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Country Manager Field.")

    asst_manager = fields.Char(string="Asst.Country Manager")

    @api.onchange('asst_manager')
    def caps_asst_manager(self):
        if self.asst_manager:
            self.asst_manager = str(self.asst_manager).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_manager):
                    raise ValidationError("Numbers are not allowed in this Asst.Country Manager Field.")

    foreign_nsnp_corp_id = fields.Many2one(comodel_name='client.profile', string="Foreign NSNP")


class ForeignCorp(models.Model):
    _name = 'foreign.corp'
    _description = "Branch of Foreign Corp"

    name = fields.Char(string="Country Manager")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Country Manager Field.")

    asst_manager = fields.Char(string="Asst.Country Manager")

    @api.onchange('asst_manager')
    def caps_asst_manager(self):
        if self.asst_manager:
            self.asst_manager = str(self.asst_manager).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_manager):
                    raise ValidationError("Numbers are not allowed in this Asst.Country Manager Field.")

    foreign_corp_id = fields.Many2one(comodel_name='client.profile', string="Foreign Corporation")


class GeneralPartnership(models.Model):
    _name = 'general.partnership'
    _description = "General Partnership"

    name = fields.Char(string="Managing Partner")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Managing Partner Field.")

    partner = fields.Char(string="Partner")

    @api.onchange('partner')
    def caps_partner(self):
        if self.partner:
            self.partner = str(self.partner).title()
            for record in self:
                if any(char.isdigit() for char in record.partner):
                    raise ValidationError("Numbers are not allowed in this Partner Field.")

    general_partnership_id = fields.Many2one(comodel_name='client.profile', string="General Partnership")


class GeneralProfessionalPartnership(models.Model):
    _name = 'general.professional.partnership'
    _description = "General Professional Partnership"

    name = fields.Char(string="Managing Partner")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Managing Partner Field.")

    partner = fields.Char(string="Partner")

    @api.onchange('partner')
    def caps_partner(self):
        if self.partner:
            self.partner = str(self.partner).title()
            for record in self:
                if any(char.isdigit() for char in record.partner):
                    raise ValidationError("Numbers are not allowed in this Partner Field.")

    general_professional_partnership_id = fields.Many2one(comodel_name='client.profile', string="Professional")


class RepresentativeOffice(models.Model):
    _name = 'representative.office'
    _description = "Representative Office"

    name = fields.Char(string="Country Manager")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Country Manager Field.")

    asst_manager = fields.Char(string="Asst.Country Manager")

    @api.onchange('asst_manager')
    def caps_asst_manager(self):
        if self.asst_manager:
            self.asst_manager = str(self.asst_manager).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_manager):
                    raise ValidationError("Numbers are not allowed in this Asst.Country Manager Field.")

    representative_office_id = fields.Many2one(comodel_name='client.profile', string="Representative")


class RoqhForeignCorp(models.Model):
    _name = 'roqh.foreign.corp'
    _description = "ROQH of Foreign Corp"

    name = fields.Char(string="Country Manager")

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Country Manager Field.")

    asst_manager = fields.Char(string="Asst.Country Manager")

    @api.onchange('asst_manager')
    def caps_asst_manager(self):
        if self.asst_manager:
            self.asst_manager = str(self.asst_manager).title()
            for record in self:
                if any(char.isdigit() for char in record.asst_manager):
                    raise ValidationError("Numbers are not allowed in this Asst.Country Manager Field.")

    roqh_foreign_corp_id = fields.Many2one(comodel_name='client.profile', string="ROHQ")


class SoleProprietor(models.Model):
    _name = 'sole.proprietor'
    _description = "Sole Proprietor"

    name = fields.Char(string='Proprietor/Proprietress')

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).title()
            for record in self:
                if any(char.isdigit() for char in record.name):
                    raise ValidationError("Numbers are not allowed in this Proprietor/Proprietress Field.")

    sole_proprietor_id = fields.Many2one(comodel_name='client.profile', string="Proprietor/Proprietress")
