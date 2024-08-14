import datetime
from odoo import fields, models, api


class FaMonitoringByDepartmentWizard(models.TransientModel):
    _name = "fa.monitoring.by.dep.wizard"
    _description = "Fixed Assets Monitoring By Department Report"

    departments = fields.Many2many(string="Department(s):", comodel_name="hr.department")
    department_name = fields.Char(string="DepName", related="departments.name", readonly=True)
    department_id = fields.Integer(string="DepID", related="departments.id", store=True)
    date_filter = fields.Date(string="As of", default=False)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'department': self.departments,
                'department_id': self.departments.ids,
                'department_name': self.department_name,
                'date_filter': self.date_filter,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('onehr_fixed_assets.fa_monitoring_by_dep_report').report_action(self, data=data)

    def button_export_html(self):
        departments = self.departments.ids
        # date = self.date_issued
        date_filter = self.date_filter
        date_now = datetime.datetime.now().date()
        company_id = self.env.company.id
        department_ids = str(departments)[1:-1]

        if departments and date_filter is False:
            domain = [('company_id', '=', company_id), ('hr_department_id', 'in', departments),
                      ('cancelled', '!=', 'true'), ('hr_department_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Department"
        elif department_ids == '' and date_filter:
            domain = [('company_id', '=', company_id), ('cancelled', '!=', 'true'), ('date_issued', '>=', date_filter),
                      ('date_issued', '<=', date_now), ('hr_department_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Department As of " + str(date_now)
        elif department_ids and date_filter:
            domain = [('hr_department_id', 'in', departments), ('company_id', '=', company_id),
                      ('cancelled', '!=', 'true'), ('date_issued', '>=', date_filter), ('date_issued', '<=', date_now),
                      ('hr_department_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Department As of " + str(date_now)
        else:
            domain = [('company_id', '=', company_id), ('cancelled', '!=', 'true'), ('hr_department_id', '!=', '0')]
            name = "Fixed Assets Monitoring by Department - All "

        return {
            "name": name,
            "type": "ir.actions.act_window",
            "res_model": "onehr.fixed.assets",
            "views": [[self.env.ref("onehr_fixed_assets.fa_tree").id, "tree"]],
            "domain": domain,
            "context": {'search_default_group_dep_name': 1, 'group_by': 'hr_department_id'}
        }


class FaMonitoringByDepartmentResults(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.onehr_fixed_assets.fa_monitoring_by_dep_report_view'
    _description = "Fixed Assets Monitoring by Department"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_filter = data['form']['date_filter']
        department_id = data['form']['department_id']
        department_ids = str(department_id)[1:-1]
        date_now = datetime.datetime.now().date()

        if department_ids and date_filter is False:
            sql_cmd = """
             SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, a.asset_qty, b.name as department, a.cancelled
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_department b on a.hr_department_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
                    WHERE a.hr_department_id != 0 AND a.hr_department_id in (%s) AND a.company_id = %s AND a.cancelled = false
                    ORDER BY a.hr_department_id, b.name, a.date_issued
                """ % (department_ids, self.env.company.id)
            header = ''
        elif department_ids == '' and date_filter:
            sql_cmd = """
             SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, a.asset_qty, b.name as department, a.cancelled
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_department b on a.hr_department_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
                    WHERE a.hr_department_id != 0 AND a.company_id = %s AND a.cancelled = false AND a.date_issued BETWEEN '%s'::DATE AND '%s'::DATE
                    ORDER BY a.hr_department_id, b.name, a.date_issued
                """ % (self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        elif department_ids and date_filter:
            sql_cmd = """
             SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, a.asset_qty, b.name as department, a.cancelled
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_department b on a.hr_department_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
                    WHERE a.hr_department_id != 0 AND a.hr_department_id in (%s) AND a.company_id = %s AND a.cancelled = false AND a.date_issued BETWEEN '%s'::DATE AND '%s'::DATE
                    ORDER BY a.hr_department_id, b.name, a.date_issued
                """ % (department_ids, self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        else:
            sql_cmd = """
             SELECT a.id, a.company_id, a.date_issued, a.name as asset_code, a.short_description, a.full_description, a.asset_qty, b.name as department, a.cancelled
                    FROM onehr_fixed_assets a 
                    LEFT JOIN hr_department b on a.hr_department_id = b.id
                    LEFT JOIN onehr_fa_status c on a.status = c.id
                    WHERE a.company_id = %s AND a.cancelled = false AND a.hr_department_id != 0
                    ORDER BY a.hr_department_id, b.name, a.date_issued
                """ % self.env.company.id
            header = ''
        self.env.cr.execute(sql_cmd)
        sql_result = self.env.cr.dictfetchall()
        docs = []
        if sql_result is not None:
            for r in sql_result:
                docs.append({
                    'department': r['department'],
                    'date_issued': r['date_issued'],
                    'asset_code': r['asset_code'],
                    'short_description': r['short_description'],
                    'full_description': r['full_description'],
                    'asset_qty': r['asset_qty'],
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
