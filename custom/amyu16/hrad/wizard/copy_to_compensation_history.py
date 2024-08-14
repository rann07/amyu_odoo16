from odoo import fields, models


class CopyToCompensationHistory(models.TransientModel):
    _name = "copy.to.compensation.history"
    _description = "Copy to compensation history"

    name = fields.Date(string="Date of effectivity", required=True)

    def button_copy_to_history(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 Employee is expected"
        e_obj = self.env['hr.employee'].browse(ids)
        rate_history = [{
            'monthly_rate': e_obj.monthly_rate,
            'semi_monthly_rate': e_obj.semi_monthly_rate,
            'weekly_rate': e_obj.weekly_rate,
            'daily_rate': e_obj.daily_rate,
            'hourly_rate': e_obj.hourly_rate,
            'monthly_cola': e_obj.monthly_cola,
            'semi_monthly_cola': e_obj.semi_monthly_cola,
            'weekly_cola': e_obj.weekly_cola,
            'daily_cola': e_obj.daily_cola,
            'hourly_cola': e_obj.hourly_cola,
            'allow_misc': e_obj.allow_misc,
            'allow_meal': e_obj.allow_meal,
            'allow_transpo': e_obj.allow_transpo,
            'tm_monthly': e_obj.tm_monthly,
            'tm_semi_monthly': e_obj.tm_semi_monthly,
            'tm_weekly': e_obj.tm_weekly,
            'employee_id': e_obj.id,
            'doe': self.name}]
        hist_obj = self.env['hr.employee.rates.history']
        hist_rec = hist_obj.search([
            ('monthly_rate', '=', e_obj.monthly_rate),
            ('semi_monthly_rate', '=', e_obj.semi_monthly_rate),
            ('weekly_rate', '=', e_obj.weekly_rate),
            ('daily_rate', '=', e_obj.daily_rate),
            ('hourly_rate', '=', e_obj.hourly_rate),
            ('monthly_cola', '=', e_obj.monthly_cola),
            ('semi_monthly_cola', '=', e_obj.semi_monthly_cola),
            ('weekly_cola', '=', e_obj.weekly_cola),
            ('daily_cola', '=', e_obj.daily_cola),
            ('hourly_cola', '=', e_obj.hourly_cola),
            ('allow_misc', '=', e_obj.allow_misc),
            ('allow_meal', '=', e_obj.allow_meal),
            ('allow_transpo', '=', e_obj.allow_transpo),
            ('tm_monthly', '=', e_obj.tm_monthly),
            ('tm_semi_monthly', '=', e_obj.tm_semi_monthly),
            ('tm_weekly', '=', e_obj.tm_weekly),
            ('employee_id', '=', e_obj.id),
            ('doe', '=', self.name)
        ])
        if not hist_rec:
            hist_obj.create(rate_history)
