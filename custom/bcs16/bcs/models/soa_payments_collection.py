from odoo import fields, models, api


class PaymentsCollection(models.Model):
    _name = 'soa.payments.collection'
    _description = "Payments Collection connected to AR Journal"

    collection_id = fields.Many2one(comodel_name='bcs.collection', required=True)
    ar_journal_id = fields.Many2one(comodel_name='soa.ar.journal', required=True,
                                    domain="[('id', 'in', context.get('ar_journal_ids', []))]")
    journal_index = fields.Integer(required=True)
    amount = fields.Float(compute='_compute_amount')

    @api.depends("collection_id.amount")
    def _compute_amount(self):
        for record in self:
            if record.manual_posting:
                record.amount = record.manual_amount
            else:
                record.amount = record.collection_id.amount

    manual_amount = fields.Float()
    manual_posting = fields.Boolean(default=False)

    # @api.onchange('manual_amount')
    # def _onchange_manual_amount(self):
    #     self.amount = self.manual_amount

    @api.model
    def create(self, vals):
        vals['journal_index'] = self.ar_journal_id.pc_ids_count + 1
        res = super(PaymentsCollection, self).create(vals)

        if res and res.manual_posting:
            res.amount = res.manual_amount
            res.collection_id.unissued_amount_for_ar -= res.amount
            res.ar_journal_id.new_manual_posting(res)

        return res

    name = fields.Char(compute="_compute_name")

    @api.depends("collection_id.date_collected", "collection_id.bank", "collection_id.payment_collection")
    def _compute_name(self):
        for record in self:
            if not record.collection_id: continue
            record.name = record.collection_id.date_collected.strftime("%b %Y") + ' | ' \
                          + dict(record.collection_id._fields['payment_collection'].selection).get(
                record.collection_id.payment_collection) \
                          + ' - ' + (
                              'Cash' if record.collection_id.payment_mode == 'cash' else record.collection_id.bank.name)
