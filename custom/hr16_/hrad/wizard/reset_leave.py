from odoo import fields, models


class HrResetLeave(models.TransientModel):
    _name = "hr.reset.leave"
    _description = "Resetting of Leave"

    new_balance = fields.Float(string="New balance")

    def reset_leave(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 Employee Leave Master is expected"
        leave_master_obj = self.env['hr.employee.leave.master'].browse(ids)
        if leave_master_obj:
            for lm in leave_master_obj:
                self.env['hr.employee.leave.reset'].create({
                    'hr_employee_id': lm.hr_employee_id.id,
                    'old_balance': lm.current_balance,
                    'new_balance': self.new_balance})
                lm.write({'current_balance': self.new_balance})
