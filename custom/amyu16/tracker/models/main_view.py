from odoo import models, fields, api, exceptions


class MainView(models.Model):
    _name = 'main.view'
    _description = "FSMS Monitoring"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'write_date'

    name = fields.Char(string="Client Name", required=True)

    @api.onchange('name')
    def caps_name(self):
        if self.name:
            self.name = str(self.name).upper()

    user_id = fields.Many2one(string="Associate", comodel_name='res.users', default=lambda self: self.env.user,
                              tracking=True)
    team_id = fields.Many2one(string="Team", comodel_name='team.group')
    supervisor_id = fields.Many2one(string="Supervisor", related="team_id.supervisor_id")
    manager_id = fields.Many2one(string="Manager", related="team_id.manager_id")
    partners_id = fields.Many2one(string="Partner", related="team_id.partners_id")

    STATES = [('draft', 'Client List'), ('preparation', 'Preparation'), ('checking', 'Checking'), ('review', 'Review'),
              ('initial_approval', 'Init. Approval'), ('proofread', 'Proofread'),
              ('final_checking', 'FNL Checking'), ('final_review', 'FNL Review'),
              ('final_approval', 'FNL Approval'), ('final_proofread', 'FNL Proofread'),
              ('iar_review', 'IAR Review'), ('printing', 'Printing'), ('sorting', 'Sorting'),
              ('qcc', 'Quality Control Check'), ('filing', 'Filing'), ('filed', 'Filed')]
    state = fields.Selection(STATES, string="Status", default='draft', tracking=True,
                             group_expand='_expand_states', index=True)

    def write(self, values):
        old_states = {rec.id: rec.state for rec in self}
        res = super(MainView, self).write(values)
        for record in self:
            if 'state' in values and record.state != old_states.get(record.id):
                self.env['state.history'].create({
                    'object_id': record.id,
                    'state': record.state,
                })
        return res

    # @api.onchange('state')
    # def _check_state_transition(self):
    #     valid_transitions = {
    #         'draft': ['preparation'],
    #         'preparation': ['checking'],
    #         'checking': ['review'],
    #         'review': ['initial_approval'],
    #         'initial_approval': ['proofread'],
    #         'proofread': ['final_checking'],
    #         'final_checking': ['final_review'],
    #         'final_review': ['final_approval'],
    #         'final_approval': ['final_proofread'],
    #         'final_proofread': ['iar_review'],
    #         'iar_review': ['printing'],
    #         'printing': ['sorting'],
    #         'sorting': ['qcc'],
    #         'qcc': ['filing'],
    #         'filing': ['filed'],
    #         'filed': []  # No further transitions allowed from 'filed'
    #     }
    #
    #     current_state = self._origin.state if self._origin else False
    #     new_state = self.state
    #
    #     if current_state and new_state not in valid_transitions.get(current_state, []):
    #         raise exceptions.ValidationError('Invalid movement transition')

    date = fields.Date(string="Time")
    order = fields.Integer(string='Order', default=0)

    @api.onchange('state')
    def onchange_state(self):
        if self.state in ['draft', 'preparation', 'checking', 'review', 'initial_approval', 'proofread']:
            # Move record down in the list by increasing order
            self.order += 1
        elif self.state in ['final_checking', 'final_review', 'final_approval', 'final_proofread', 'iar_review',
                            'printing', 'sorting', 'qcc', 'filing', 'filed']:
            # Reset the order for records that reached final states
            self.order = 0

    priority = fields.Selection([('0', 'Normal'), ('1', 'Low'), ('2', 'High'), ('3', 'Very High')], string="Priority")

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    date_start = fields.Datetime(string="Date Start")
    date_end = fields.Datetime(string="Date End")

    @api.model
    def create(self, vals):
        if vals.get('state') == 'preparation':
            vals['date_start'] = fields.Datetime.now()
        else:
            if vals.get('state') == 'filed':
                vals['date_end'] = fields.Datetime.now()
        return super(MainView, self).create(vals)

    def write(self, vals):
        if vals.get('state') == 'preparation':
            vals['date_start'] = fields.Datetime.now()
        else:
            if vals.get('state') == 'filed':
                vals['date_end'] = fields.Datetime.now()
        return super(MainView, self).write(vals)

    total_time = fields.Integer(string="Total Time", compute='_compute_total_time', store=True)
    revision_id = fields.Many2one(comodel_name='revision.status', string="Status", tracking=True)

    @api.onchange('state')
    def clear_revision_id(self):
        if self.state != 'draft':
            self.revision_id = [(5, 0, 0)]

    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        for record in self:
            if record.date_start and record.date_end:
                time_delta = record.date_end - record.date_start
                total_seconds = time_delta.total_seconds()
                total_hours = total_seconds / 3600
                record.total_time = total_hours
            else:
                record.total_time = 0.0

    # LABEL
    label_note_ids = fields.Many2many(string="Label", comodel_name='label.maintenance', tracking=True)

    state_ids = fields.Many2many(string="Sign Off", comodel_name='state.labels', tracking=True)
    progress_state = fields.Float(string='Progress', compute='_compute_progress', store=True)

    @api.depends('state_ids')
    def _compute_progress(self):
        total_records = len(self.env['state.labels'].search([]))  # Total number of choices
        if total_records > 0:
            selected_records = len(self.state_ids)  # Number of selected choices
            self.progress_state = (selected_records / total_records) * 100
        else:
            self.progress_state = 0

    label_printer_ids = fields.Many2many(string="Checklist", comodel_name='label.printer', )
    attachment_printer_ids = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_printer_rel",
                                              column1="m2m_id", column2="attachment_id",
                                              string="Attachment`")
    printer_filename = fields.Char(string="File")
    progress_printer = fields.Float(string='Printer Checklist', compute='_compute_progress_printer', store=True)

    @api.depends('label_printer_ids')
    def _compute_progress_printer(self):
        total_records = len(self.env['label.printer'].search([]))  # Total number of choices
        if total_records > 0:
            selected_records = len(self.label_printer_ids)  # Number of selected choices
            self.progress_printer = (selected_records / total_records) * 100
        else:
            self.progress_printer = 0

    label_sorter_ids = fields.Many2many(string="Checklist", comodel_name='label.sorter')
    attachment_sorter = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_sorter_rel",
                                         column1="m2m_id", column2="attachment_id",
                                         string="Attachment`")
    sorter_filename = fields.Char(string="File")
    progress_sorter = fields.Float(string='Sorter Progress', compute='_compute_progress_sorter', store=True)

    @api.depends('label_sorter_ids')
    def _compute_progress_sorter(self):
        total_records = len(self.env['label.sorter'].search([]))  # Total number of choices
        if total_records > 0:
            selected_records = len(self.label_sorter_ids)  # Number of selected choices
            self.progress_sorter = (selected_records / total_records) * 100
        else:
            self.progress_sorter = 0

    label_qcc_ids = fields.Many2many(string="Quality Check Control Checklist",
                                     comodel_name='label.qcc')
    attachment_qcc = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_qcc_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Attachment`")
    qcc_filename = fields.Char(string="File")
    progress_qcc = fields.Float(string='Progress', compute='_compute_progress_qcc', store=True)

    @api.depends('label_qcc_ids')
    def _compute_progress_qcc(self):
        total_records = len(self.env['label.qcc'].search([]))  # Total number of choices
        if total_records > 0:
            selected_records = len(self.label_qcc_ids)  # Number of selected choices
            self.progress_qcc = (selected_records / total_records) * 100
        else:
            self.progress_qcc = 0

    label_bir_ids = fields.Many2many(string="B.I.R Checklist", comodel_name='label.bir')
    attachment_bir = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_bir_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Attachment`")
    bir_filename = fields.Char(string="File")
    progress_bir = fields.Float(string='Progress', compute='_compute_progress_bir', store=True)

    @api.depends('label_bir_ids')
    def _compute_progress_bir(self):
        total_records = len(self.env['label.bir'].search([]))  # Total number of choices
        if total_records > 0:
            selected_records = len(self.label_bir_ids)  # Number of selected choices
            self.progress_bir = (selected_records / total_records) * 100
        else:
            self.progress_bir = 0

    label_sec_ids = fields.Many2many(string="S.E.C Checklist", comodel_name='label.sec')
    attachment_sec = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_sec_rel",
                                      column1="m2m_id", column2="attachment_id",
                                      string="Attachment`")
    sec_filename = fields.Char(string="File")
    progress_sec = fields.Float(string='Progress', compute='_compute_progress_sec', store=True)

    @api.depends('label_sec_ids')
    def _compute_progress_sec(self):
        total_records = len(self.env['label.sec'].search([]))  # Total number of choices
        if total_records > 0:
            selected_records = len(self.label_sec_ids)  # Number of selected choices
            self.progress_sec = (selected_records / total_records) * 100
        else:
            self.progress_sec = 0

    # def get_form_action(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'label.printer',  # Replace with the model you want to open
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'target': 'new',
    #     }
