import datetime
from odoo import fields, models, api


class FaMonitoringByGroupWizard(models.TransientModel):
    _name = "fa.monitoring.by.group.wizard"
    _description = "Fixed Assets Monitoring By Group Report"

    groups = fields.Many2many(comodel_name="onehr.fa.group", string="Group(s):")
    group_name = fields.Char(string="GroupName", related="groups.name", readonly=True)
    group_id = fields.Integer(string="Group", related="groups.id", store=True)
    date_filter = fields.Date(string="As of", default=False)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'groups': self.groups,
                'group_id': self.groups.ids,
                'group_name': self.group_name,
                'date_filter': self.date_filter,
            },
        }
        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        return self.env.ref('onehr_fixed_assets.fa_monitoring_by_group_report').report_action(self, data=data)

    def button_export_html(self):
        groups = self.groups.ids
        date_filter = self.date_filter
        date_now = datetime.datetime.now().date()
        company_id = self.env.company.id
        group_ids = str(groups)[1:-1]

        if groups and date_filter is False:
            domain = [('company_id', '=', company_id), ('group_id', 'in', groups), ('cancelled', '!=', 'true')]
            name = "Fixed Assets Monitoring by Group"
        elif group_ids == '' and date_filter:
            domain = [('company_id', '=', company_id), ('cancelled', '!=', 'true'), ('date_issued', '>=', date_filter),
                      ('date_issued', '<=', date_now)]
            name = "Fixed Assets Monitoring by Group As of " + str(date_now)
        elif group_ids and date_filter:
            domain = [('group_id', 'in', groups), ('company_id', '=', company_id), ('cancelled', '!=', 'true'),
                      ('date_issued', '>=', date_filter), ('date_issued', '<=', date_now)]
            name = "Fixed Assets Monitoring by Group As of " + str(date_now)
        else:
            domain = [('company_id', '=', company_id), ('cancelled', '!=', 'true')]
            name = "Fixed Assets Monitoring by Group - All "

        return {
            "name": name,
            "type": "ir.actions.act_window",
            "res_model": "onehr.fixed.assets",
            "views": [[self.env.ref("onehr_fixed_assets.fa_tree").id, "tree"]],
            "domain": domain,
            "context": {'search_default_group_group_name': 1, 'group_by': 'group_id'}
        }


class FaMonitoringByGroupResults(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.onehr_fixed_assets.fa_monitoring_by_group_report_view'
    _description = "Fixed Assets Monitoring by Group"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_filter = data['form']['date_filter']
        group_id = data['form']['group_id']
        group_ids = str(group_id)[1:-1]
        date_now = datetime.datetime.now().date()

        if group_ids and date_filter is False:
            sql_cmd = """
                     SELECT a.id, a.company_id, a.group_id, a.date_issued, a.name as asset_code, c.name as group, a.short_description, a.full_description, a.asset_qty, b.name as custodian, 
            		 		b.job_title, a.cancelled, d.name as hr_department_name
                            FROM onehr_fixed_assets a 
                            LEFT JOIN hr_employee b on a.hr_employee_id = b.id
            			    LEFT JOIN onehr_fa_group c on a.group_id = c.id
            				LEFT JOIN hr_department d on a.hr_department_id = d.id
                            WHERE a.group_id in (%s) AND a.company_id = %s AND a.cancelled = false
                            ORDER BY a.group_id, b.name, a.date_issued
                        """ % (group_ids, self.env.company.id)
            header = ''
        elif group_ids == '' and date_filter:
            sql_cmd = """
                     SELECT a.id, a.company_id, a.group_id, a.date_issued, a.name as asset_code, c.name as group, a.short_description, a.full_description, a.asset_qty, b.name as custodian, 
            		 		b.job_title, a.cancelled, d.name as hr_department_name
                            FROM onehr_fixed_assets a 
                            LEFT JOIN hr_employee b on a.hr_employee_id = b.id
            			    LEFT JOIN onehr_fa_group c on a.group_id = c.id
            				LEFT JOIN hr_department d on a.hr_department_id = d.id
                            WHERE a.company_id = %s AND a.cancelled = false AND a.date_issued BETWEEN '%s'::DATE AND '%s'::DATE
                            ORDER BY a.group_id, b.name, a.date_issued
                        """ % (self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        elif group_ids and date_filter:
            sql_cmd = """
                         SELECT a.id, a.company_id, a.group_id, a.date_issued, a.name as asset_code, c.name as group, a.short_description, a.full_description, a.asset_qty, b.name as custodian, 
                		 		b.job_title, a.cancelled, d.name as hr_department_name
                                FROM onehr_fixed_assets a 
                                LEFT JOIN hr_employee b on a.hr_employee_id = b.id
                			    LEFT JOIN onehr_fa_group c on a.group_id = c.id
                				LEFT JOIN hr_department d on a.hr_department_id = d.id
                                WHERE a.group_id in (%s) AND a.company_id = %s AND a.cancelled = false AND a.date_issued BETWEEN '%s'::DATE AND '%s'::DATE
                                ORDER BY a.group_id, b.name, a.date_issued
                            """ % (group_ids, self.env.company.id, date_filter, date_now)
            header = "As of " + str(date_filter)
        else:
            sql_cmd = """
                     SELECT a.id, a.group_id, a.date_issued, a.name as asset_code, c.name as group, a.short_description, a.full_description, a.asset_qty, b.name as custodian, 
            		 		b.job_title, a.cancelled, d.name as hr_department_name
                            FROM onehr_fixed_assets a 
                            LEFT JOIN hr_employee b on a.hr_employee_id = b.id
            			    LEFT JOIN onehr_fa_group c on a.group_id = c.id
            				LEFT JOIN hr_department d on a.hr_department_id = d.id
                            WHERE a.company_id = %s AND a.cancelled = false
                            ORDER BY a.group_id, b.name, a.date_issued
                        """ % self.env.company.id
            header = ''
        self.env.cr.execute(sql_cmd)
        sql_result = self.env.cr.dictfetchall()
        docs = []
        if sql_result is not None:
            for r in sql_result:
                if r['custodian'] is None:
                    assigned = r['hr_department_name']
                    docs.append({
                        'group': r['group'],
                        'group_id': r['group_id'],
                        'date_issued': r['date_issued'],
                        'asset_code': r['asset_code'],
                        'short_description': r['short_description'],
                        'full_description': r['full_description'],
                        'asset_qty': r['asset_qty'],
                        'custodian': assigned,
                        'job_title': r['job_title'],
                    })
                else:
                    docs.append({
                        'group': r['group'],
                        'group_id': r['group_id'],
                        'date_issued': r['date_issued'],
                        'asset_code': r['asset_code'],
                        'short_description': r['short_description'],
                        'full_description': r['full_description'],
                        'asset_qty': r['asset_qty'],
                        'custodian': r['custodian'],
                        'job_title': r['job_title'],
                    })
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
