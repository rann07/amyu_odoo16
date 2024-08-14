import datetime
from odoo import fields, models, api


class CancelledFaWizard(models.TransientModel):
    _name = "cancelled.fa.wizard"
    _description = "Cancelled Fixed Assets Report"

    date_filter = fields.Date(string="As of", default=False)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_filter': self.date_filter,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('onehr_fixed_assets.cancelled_fa_report').report_action(self, data=data)

    def button_export_html(self):
        date_filter = self.date_filter
        date_now = datetime.datetime.now().date()
        company_id = self.env.company.id

        if date_filter:
            domain = [('company_id', '=', company_id), ('cancelled', '=', 'true'),
                      ('date_cancelled', '>=', date_filter), ('date_cancelled', '<=', date_now)]
            name = "Cancelled Fixed Assets As of" + str(date_filter)
        else:
            domain = [('company_id', '=', company_id), ('cancelled', '=', 'true')]
            name = "Cancelled Fixed Assets - All"
        return {
            "name": name,
            "type": "ir.actions.act_window",
            "res_model": "onehr.fixed.assets",
            "views": [[self.env.ref("onehr_fixed_assets.fa_tree").id, "tree"]],
            "domain": domain,
            "context": {'search_default_group_emp_name': 1, 'search_default_group_employee_id': 1}
        }


class CancelledFaReports(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.onehr_fixed_assets.cancelled_fa_report_view'
    _description = "List of Cancelled Fixed Assets"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_filter = data['form']['date_filter']
        date_now = datetime.datetime.now().date()

        if date_filter:
            sql_cmd = """
            SELECT a.id, a.company_id, a.name as asset_code, a.asset_qty, b.name as custodian, a.full_description, a.remarks, a.date_cancelled
            FROM onehr_fixed_assets a
            LEFT JOIN hr_employee b on a.hr_employee_id = b.id
            WHERE a.company_id = %s AND a.cancelled = true AND a.date_cancelled BETWEEN '%s'::DATE AND '%s'::DATE
            ORDER BY a.date_cancelled
            """ % (self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        else:
            sql_cmd = """
            SELECT a.id, a.company_id, a.name as asset_code, a.asset_qty, b.name as custodian, a.full_description, a.remarks, a.date_cancelled
            FROM onehr_fixed_assets a
            LEFT JOIN hr_employee b on a.hr_employee_id = b.id
            WHERE a.company_id = %s AND a.cancelled = true
            ORDER BY a.date_cancelled
            """ % self.env.company.id
            header = ''
        self.env.cr.execute(sql_cmd)
        sql_result = self.env.cr.dictfetchall()
        docs = []
        if sql_result:
            for r in sql_result:
                docs.append({
                    'asset_code': r['asset_code'],
                    'full_description': r['full_description'],
                    'custodian': r['custodian'],
                    'asset_qty': r['asset_qty'],
                    'date_cancelled': r['date_cancelled'],
                    'remarks': r['remarks'],
                })
        print(self.env.company.report_header, )
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'header': header,
            'date_now': date_now,
            'company_id': self.env.company,
            'company_logo': self.env.company.logo,
            'company_name': self.env.company.name,
            'docs': docs,
        }
