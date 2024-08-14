import logging, datetime, math
from odoo import api, fields, models

class Liaison(models.Model):
    _name = 'liaison'
    _description = 'Liaison Record for the errands'
    _sql_constraints = [
        (
            'unique_employee_id', 
            'unique(employee_id)',
            'Liaison is already added.'
        )
    ]

    employee_id = fields.Many2one('hr.employee', 
                                  domain=f"[('job_id.name','ilike', 'Liaison')]", 
                                  copy=False, index=True, required=True, ondelete='restrict')
    location_id = fields.Many2one('location', string="Assigned Location")
    name = fields.Char(compute="_compute_name", string="Displayed Name", readonly=True)
    

    @api.depends("employee_id.fullname")
    def _compute_name(self):
        for record in self:
            record.name = record.employee_id.fullname

    
    