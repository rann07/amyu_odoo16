from odoo import fields, models
import datetime, calendar

YEARS = [('2023', '2023')]


class ComputePayroll(models.TransientModel):
    _name = "compute.payroll.executives"

    month_of = fields.Selection(string="Month", selection=[
        ('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'),
        ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'Semptember'),
        ('October', 'October'), ('November', 'November'), ('December', 'December'),
    ], required=True, default=lambda self: calendar.month_name[datetime.date.today().month])
    year_of = fields.Selection(string="Year", selection=YEARS, required=True,
                               default=lambda self: str(datetime.date.today().year))
    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)

    def init(self):
        curr_year = datetime.date.today().year
        for n in range(curr_year - 2023):
            YEARS.append((str(2023 + n), str(2023 + n)))

    def action_compute_payroll(self):
        return
        # return {
        #     "name": "Computed Time Card " + str(self.from_date) + "-" + str(self.to_date),
        #     "type": "ir.actions.act_window",
        #     "res_model": "hr.time.card",
        #     "views": [[self.env.ref("onehr_tk.hr_time_card_tree").id, "tree"]],
        #     "domain": [('date', '>=', self.from_date), ('date', '<=', self.to_date)],
        #     "context": {'search_default_group_employee_id':1}
        # }
