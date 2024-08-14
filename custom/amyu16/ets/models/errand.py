
import datetime
from odoo import api, fields, models
from lxml import etree

class Errand(models.Model):
    _name = 'errand'
    _description = 'Errand Record'

    # Values inside each array as dict value is in sequence
    CHOICES = {
        'type_of_request': [
            ('delivery', 'Delivery'), 
            ('pickup', 'Pick Up'),
            ('filing', 'Govt Filing'),
            ('payment', 'Payment')
        ],
        'status': [ 
            ('draft', 'Draft'),
            ('pending', 'Pending'), 
            ('for_approval', 'For Approval'),
            ('in_process', 'In Process'),
            ('closed', 'Closed')
        ], 
        'delivery_item': [
            ('transmittal', 'Documents for Transmittal'), 
            ('engagement', 'Engagement Proposal'),
            ('billing', 'Billing Statement'),
            ('others', 'Others'),
        ],
        'pickup_item': [
            ('documents', 'Documents'), 
            ('check', 'Check for Payment'),
            ('collection', 'Collection Check'),
            ('others', 'Others'),
        ],
        'documents_for_filing': [
            ('tax_returns-submissions', 'Tax Returns/Submissions'), 
            ('sec_filing', 'SEC Filing'),
            ('permits-license', 'Permits/License'),
            ('statutories', 'Statutories')
        ],
        'mode_of_payment': [
            ('cash', 'Cash'), 
            ('check', 'Check'),
        ],
    }    

    ctrl_no = fields.Char(string='Ctrl No.') # auto generated
    status = fields.Selection(CHOICES['status'], default='draft')
    date_requested = fields.Date() # validation, past to present only
    requested_by = fields.Many2one('hr.employee') # many to one - registered user
    client = fields.Char(string='Client') # many to one - all the clients from cpms
    deadline = fields.Date() # validation, future only (unless rimd)
    location = fields.Many2one('location') # many to one - location table
    liaison = fields.Many2one('liaison', string='Liaison') # many to one - liaison table

    # form highlight
    # is_govt_transaction = fields.Boolean(default=False, string='Government Transaction')
    type_of_request = fields.Selection(CHOICES['type_of_request'], default='delivery', string='Request')
    
    company_agency_payee = fields.Char(compute='_compute_company_agency_payee', string='Company/Agency/Payee')
    
    # delivery and pickup; hidden
    company_for_delivery_pickup = fields.Char(string='Company') # many2one of clients from cpms
    address = fields.Char() # optional
    contact_person = fields.Char() # optional
    contact_number = fields.Char() # optional # validation, must be a valid number
    delivery_item = fields.Selection(CHOICES['delivery_item']) # should be radio button, with field on Others???
    pickup_item = fields.Selection( CHOICES['pickup_item']) # should be radio button, with field on Others???
    
    # filing; hidden
    agency_for_filing = fields.Char(string="Agency") # auto suggest?
    branch_rdo = fields.Char() # auto suggest?
    with_payment = fields.Boolean(default=False)
    documents_for_filing = fields.Selection(CHOICES['documents_for_filing'])# should be radio button, with field???
    
    # payment; hidden
    payee_for_payment = fields.Char(string="Payee") # auto suggest?
    amount = fields.Char()
    mode_of_payment = fields.Selection(CHOICES['mode_of_payment'])
    purpose = fields.Char() # auto suggest?
    issuing_bank_branch = fields.Char()
    check_number = fields.Char()
    check_date = fields.Date()
    
    # other fields
    special_instructions = fields.Text(string="Instructions") # auto suggest?
    date_received = fields.Date() # optional
    received_by = fields.Char() # auto suggest?
    date_completed = fields.Date() # auto generated
    remarks = fields.Text(string="RIMD Remarks") # optional


    @api.model
    def create(self, kwargs: dict):
        """ 
        Overrides the create method of the model 
        """
        new_ctrl_no: str = Errand.generate_ctrl_no(self)
        kwargs['ctrl_no'] = new_ctrl_no
        return super(Errand, self).create(kwargs)
    
    
    # @api.model
    # def get_view(self, view_id=None, view_type='tree', **options):
    #     res = super(Errand, self).get_view(view_id=view_id, view_type=view_type)
    #     if view_type == 'tree' and view_id == 'for_approval_errand_view_tree':
    #         root = etree.fromstring(res['arch'])
    #         root.set('create', 'false')
    #         res['arch'] = etree.tostring(root)

    #     return res
    
    
    @api.onchange('client')
    def _onchange_client(self):
        if self.type_of_request in ['delivery', 'pickup']:
            self.company_for_delivery_pickup = self.client

    
    @api.onchange('location')
    def _onchange_location(self):
        """ 
        Set the assigned liaison to the default liaison of the location  
        """
        domain = [('location_id','=', self.location.id)]
        default_liaison = self.env['liaison'].search(domain)
        self.liaison = default_liaison
    
    
    @api.depends('company_for_delivery_pickup', 'agency_for_filing', 'payee_for_payment')
    def _compute_company_agency_payee(self):
        for record in self:
            if record.type_of_request in ['delivery', 'pickup']:
                record.company_agency_payee = record.company_for_delivery_pickup
            elif record.type_of_request == 'filing':
                record.company_agency_payee = record.agency_for_filing
            elif record.type_of_request == 'payment':
                record.company_agency_payee = record.payee_for_payment
    
    
    @staticmethod
    def generate_ctrl_no(errand_self) -> str:
        year_month_now: str = datetime.datetime.now().strftime('%y-%m')
        
        results = Errand.search(self=errand_self, domain=[
            ('ctrl_no', 'like', year_month_now)
        ])
        
        if len(list(results)) == 0:
            return f'{year_month_now}E{1:05d}'

        ctrl_num_list: list = [int(result.ctrl_no[-5:]) for result in results]
        ctrl_num_max: int = max(ctrl_num_list)
        next_ctrl_num = ctrl_num_max + 1

        return f'{year_month_now}E{next_ctrl_num:05d}'
    
    
    @staticmethod
    def get_default_liaison_location(liaison:str=None, location:str=None) -> str:
        Errand.get_all_liaison_location()
        return ''
    
    
    @staticmethod
    def get_all_liaison_per_location() -> dict:
        return {}
    
    
    def set_status_for_approval(self):
        if self.status == 'draft':
            needs_pending = self.delivery_item and self.delivery_item == 'transmittal' 
            self.status = 'pending' if needs_pending else 'for_approval'
        elif self.status == 'pending':
            self.status = 'for_approval'
        # return {
        #     'name': 'My Errands',
        #     'view_type': 'tree',
        #     'view_mode': 'tree',
        #     'view_id': self.env.ref('ets.errand_view_tree').id,
        #     'res_model': 'errand',
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        # }
    
    def set_status_in_process(self):
        if self.status == 'for_approval':
            self.status = 'in_process'
    
    def set_status_closed(self):
        if self.status == 'in_process':
            self.status = 'closed'
    