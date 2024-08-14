from odoo import fields, models


class ComputeTimeCard(models.TransientModel):
    _name = "compute.time.card"

    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)

    def action_compute_time_card(self):
        tc_obj = self.env['hr.time.card']

        tc_obj.compute_time_card(from_date=self.from_date, to_date=self.to_date,
                                 company_id=self.env.company.id)
        return {
            "name": "Computed Time Card " + str(self.from_date) + "-" + str(self.to_date),
            "type": "ir.actions.act_window",
            "res_model": "hr.time.card",
            "views": [[self.env.ref("onehr_tk.hr_time_card_tree").id, "tree"]],
            "domain": [('date', '>=', self.from_date), ('date', '<=', self.to_date)],
            "context": {'search_default_group_employee_id':1}
        }
