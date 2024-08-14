from odoo import models, fields, api


class ManualPosting(models.TransientModel):
    _name = 'manual.posting'

    collection_id = fields.Many2one(comodel_name='bcs.collection', required=True)
    ar_journal_id = fields.Many2one(comodel_name='soa.ar.journal',
                                    domain="[('id', 'in', context.get('ar_journal_ids', []))]", required=True, )
    journal_index = fields.Integer(required=True)
    amount = fields.Float(compute='_compute_amount')
    manual_amount = fields.Float()
    manual_posting = fields.Boolean(default=False)

    @api.depends("collection_id.amount")
    def _compute_amount(self):
        for record in self:
            if record.manual_posting:
                record.amount = record.manual_amount
            else:
                record.amount = record.collection_id.amount

    @api.model
    def create(self, vals):
        vals['journal_index'] = self.ar_journal_id.pc_ids_count + 1
        res = super(ManualPosting, self).create(vals)

        if res and res.manual_posting:
            res.amount = res.manual_amount
            res.collection_id.unissued_amount_for_ar -= res.amount
            res.ar_journal_id.new_manual_posting(res)

        return res

    name = fields.Char(compute="_compute_name")

    @api.depends("collection_id.date_collected", "collection_id.bank", "collection_id.payment_collection")
    def _compute_name(self):
        for record in self:
            if not record.collection_id:
                continue
            record.name = record.collection_id.date_collected.strftime("%b %Y") + ' | ' \
                          + dict(record.collection_id._fields['payment_collection'].selection).get(
                record.collection_id.payment_collection) \
                          + ' - ' + (
                              'Cash' if record.collection_id.payment_mode == 'cash' else record.collection_id.bank.name)
