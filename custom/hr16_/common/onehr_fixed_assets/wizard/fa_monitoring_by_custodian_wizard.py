import datetime
from odoo import fields, models, api


class FaMonitoringByCustodianWizard(models.TransientModel):
    _name = "fa.monitoring.by.custodian.wizard"
    _description = "Fixed Assets Monitoring By Custodian Report"

    custodians = fields.Many2many(comodel_name="hr.employee", string="Custodian(s):")
    custodians_name = fields.Char(string="CustodianName", related="custodians.name", readonly=True)
    custodian_id = fields.Integer(string="CustodianID", related="custodians.id", store=True)
    date_filter = fields.Date(string="As of", default=False)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'custodians': self.custodians,
                'custodian_id': self.custodians.ids,
                'custodian_name': self.custodians_name,
                'date_filter': self.date_filter,
            },
        }
        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('onehr_fixed_assets.fa_monitoring_by_cust_report').report_action(self, data=data)

    def button_export_html(self):
        custodians = self.custodians.ids
        date_filter = self.date_filter
        date_now = datetime.datetime.now().date()
        company_id = self.env.company.id
        custodian_ids = str(custodians)[1:-1]

        if custodians and date_filter is False:
            domain = [('company_id', '=', company_id), ('hr_employee_id', 'in', custodians),
                      ('cancelled', '!=', 'true'), ('hr_employee_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Custodian"
        elif custodian_ids == '' and date_filter:
            domain = [('company_id', '=', company_id), ('cancelled', '!=', 'true'), ('date_issued', '>=', date_filter),
                      ('date_issued', '<=', date_now), ('hr_employee_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Custodian As of " + str(date_now)
        elif custodian_ids and date_filter:
            domain = [('hr_employee_id', 'in', custodians), ('company_id', '=', company_id),
                      ('cancelled', '!=', 'true'), ('date_issued', '>=', date_filter), ('date_issued', '<=', date_now),
                      ('hr_employee_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Custodian As of " + str(date_now)
        else:
            domain = [('company_id', '=', company_id), ('cancelled', '!=', 'true'), ('hr_employee_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Custodian - All "

        return {
            "name": name,
            "type": "ir.actions.act_window",
            "res_model": "onehr.fixed.assets",
            "views": [[self.env.ref("onehr_fixed_assets.fa_tree").id, "tree"]],
            "domain": domain,
            "context": {'search_default_group_custodian_name': 1, 'group_by': 'hr_employee_id'}
        }


class FaMonitoringByCustodianResults(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.onehr_fixed_assets.fa_by_custodian_report_view'
    _description = "Fixed Assets by Custodian"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_filter = data['form']['date_filter']
        custodian_id = data['form']['custodian_id']
        custodian_ids = str(custodian_id)[1:-1]
        date_now = datetime.datetime.now().date()

        if custodian_ids and date_filter is False:
            sql_cmd = """
            SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, 
            a.asset_qty, a.cancelled, b.name as custodian, b.job_title, c.name as status
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_employee b on a.hr_employee_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
					WHERE a.hr_employee_id != 0 AND a.hr_employee_id in (%s) AND a.company_id = %s AND a.cancelled = false
                    ORDER BY a.hr_employee_id, b.name, a.date_issued
                """ % (custodian_ids, self.env.company.id)
            header = ''
        elif custodian_ids == '' and date_filter:
            sql_cmd = """
                    SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, 
                    a.asset_qty, a.cancelled, b.name as custodian, b.job_title, c.name as status
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_employee b on a.hr_employee_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
					WHERE a.hr_employee_id != 0 AND a.company_id = %s AND a.cancelled = false AND a.date_issued BETWEEN '%s'::DATE AND '%s'::DATE
                    ORDER BY a.hr_employee_id, b.name, a.date_issued
                 """ % (self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        elif custodian_ids and date_filter:
            sql_cmd = """
                    SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, 
                    a.asset_qty, a.cancelled, b.name as custodian, b.job_title, c.name as status
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_employee b on a.hr_employee_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
        			WHERE a.hr_employee_id != 0 AND a.hr_employee_id in (%s) AND a.company_id = %s AND a.cancelled = false AND a.date_issued BETWEEN '%s'::DATE AND '%s'::DATE
                    ORDER BY a.hr_employee_id, b.name, a.date_issued
                """ % (custodian_ids, self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        else:
            sql_cmd = """
             SELECT a.id,a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, 
             a.asset_qty, a.cancelled, b.name as custodian, b.job_title, c.name as status
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_employee b on a.hr_employee_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
                    WHERE a.company_id = %s AND a.cancelled = false AND a.hr_employee_id != 0
                    ORDER BY a.hr_employee_id, b.name, a.date_issued
                """ % self.env.company.id
            header = ''
        self.env.cr.execute(sql_cmd)
        sql_result = self.env.cr.dictfetchall()
        docs = []
        if sql_result is not None:
            for r in sql_result:
                docs.append({
                    'date_issued': r['date_issued'],
                    'asset_code': r['asset_code'],
                    'short_description': r['short_description'],
                    'full_description': r['full_description'],
                    'asset_qty': r['asset_qty'],
                    'custodian': r['custodian'],
                    'job_title': r['job_title'],
                    'status': r['status'],
                })
            else:
                print('No Results')
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
