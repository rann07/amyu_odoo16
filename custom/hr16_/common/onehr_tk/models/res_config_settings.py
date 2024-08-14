from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    cc_api_key = fields.Char(string="CrossChex API Key") # f7c3ab4f8fa2de2e8d1a52f758c33d40
    cc_secret = fields.Char(string="Secret") # 2bb19a884af8e1f1cb68452e28422d8e
    no_of_days = fields.Integer(string="Number of days", default=7)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            cc_api_key=self.env['ir.config_parameter'].sudo().get_param('onehr_tk.cc_api_key'),
            cc_secret=self.env['ir.config_parameter'].sudo().get_param('onehr_tk.cc_secret'),
            no_of_days=self.env['ir.config_parameter'].sudo().get_param('onehr_tk.no_of_days'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        cc_api_key = self.cc_api_key or False
        cc_secret = self.cc_secret or False
        no_of_days = self.no_of_days or 7
        param.set_param('onehr_tk.cc_api_key', cc_api_key)
        param.set_param('onehr_tk.cc_secret', cc_secret)
        param.set_param('onehr_tk.no_of_days', no_of_days)
