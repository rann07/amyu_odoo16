from odoo import models, fields


class SetCustodian(models.TransientModel):
    _name = "set.custodian.wiz"
    _description = "Set Custodian"

    custodian = fields.Selection(string="Assigned to", selection=[
        ("employee", "Employee"), ("department", "Department"),
        ("none", "Non-Employee"), ("unassigned", "Unassigned")
    ], default="unassigned")
    none_employee = fields.Char(string="Name")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="onehr.fa.view.all.employees")
    hr_department_id = fields.Many2one(string="Department", comodel_name="onehr.fa.view.all.departments")
    company_id = fields.Many2one(string="Business Unit", comodel_name="onehr.fa.view.all.companies")

    def set_custodian(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 Fixed Asset is expected"
        fa_obj = self.env['onehr.fixed.assets'].browse(ids)
        date_stamp = fields.Datetime.now()
        from_employee_id = fa_obj.hr_employee_id.id if fa_obj.hr_employee_id else False
        to_employee_id = self.hr_employee_id.id if self.hr_employee_id else False
        from_department_id = fa_obj.hr_department_id.id if fa_obj.hr_department_id else False
        to_department_id = self.hr_department_id.id if self.hr_department_id else False
        non_employee = self.none_employee if self.custodian == "none" else False
        fa_obj.write({'custodian': self.custodian,
                      'hr_employee_id': to_employee_id,
                      'hr_department_id': to_department_id,
                      'non_employee': non_employee})
        movement_log = [{
            "date_stamp": date_stamp,
            "user_id": self.env.user.id,
            "fa_id": fa_obj.id,
            "from_employee_id": from_employee_id,
            "to_employee_id": to_employee_id,
            "from_department_id": from_department_id,
            "to_department_id": to_department_id,
            "company_id": self.company_id.id
        }]
        move_obj = self.env['onehr.fa.movement.log']
        move_hist = move_obj.search([
            ("date_stamp", "=", date_stamp),
            ("user_id", "=", self.env.user.id),
            ("fa_id", "=", fa_obj.id)
        ])
        if not move_hist:
            move_obj.create(movement_log)
