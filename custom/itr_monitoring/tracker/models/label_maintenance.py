from odoo import models, fields


class LabelMaintenance(models.Model):
    _name = 'label.maintenance'
    _description = "Maintenance for Label Selection"

    name = fields.Char(string="Label")
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    handles = fields.Char(string="Drag and Drop")
    label_id = fields.Many2one(string="Label", comodel_name='task.view')


class LabelPrinter(models.Model):
    _name = 'label.printer'
    _description = "Printer for Label Selection"

    name = fields.Char(string="Label")
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    printer_id = fields.Many2one(string="Checklist", comodel_name='task.view')


class LabelSorter(models.Model):
    _name = 'label.sorter'
    _description = "Sorter for Label Selection"

    name = fields.Char(string="Label")
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    sorter_id = fields.Many2one(string="Checklist", comodel_name='task.view')


class LabelQcc(models.Model):
    _name = 'label.qcc'
    _description = "QCC for Label Selection"

    name = fields.Char(string="Label")
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    qcc_id = fields.Many2one(string="Checklist", comodel_name='task.view')


class LabelBir(models.Model):
    _name = 'label.bir'
    _description = "BIR for Label Selection"

    name = fields.Char(string="Label")
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    qcc_id = fields.Many2one(string="Checklist", comodel_name='task.view')


class LabelSec(models.Model):
    _name = 'label.sec'
    _description = "SEC for Label Selection"

    name = fields.Char(string="Label")
    active = fields.Boolean(string="Active")
    color = fields.Integer(string="Color")
    qcc_id = fields.Many2one(string="Checklist", comodel_name='task.view')


class RevisionStatus(models.Model):
    _name = 'revision.status'
    _description = "Ongoing Process"

    name = fields.Char(string="Name")
    color = fields.Integer(string="Color")
    revision_ids = fields.One2many(string="Name", comodel_name='task.view', inverse_name="revision_id")


class StateLabels(models.Model):
    _name = 'state.labels'
    _description = "Label of States"

    name = fields.Char(string="States")
    color = fields.Integer(string="Color")
    state_id = fields.Many2one(string="Label", comodel_name='task.view')
