from odoo import fields, models, api


class AmyuSysIncludedModules(models.Model):
    _name = 'amyusys.included.modules'
    _description = "All modules of AMYU Systems"

    name = fields.Char(required=True)
    description = fields.Text()
    module_name = fields.Char(required=True)

    def import_amyu_data(self):
        view_tree = self.env.ref('bcs.soa_ar_journal_view_tree').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name',
            'view_mode': 'tree',
            'res_model': 'bcs.billing',
            'view_id': view_tree,
            'domain': [()],
            'context': "{'create': False}"
        }
