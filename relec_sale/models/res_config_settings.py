# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_delivery_term = fields.Text(string="Sale Terms of Delivery",
                               translate=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            sale_delivery_term=ICPSudo.get_param('pyrax_sale.sale_delivery_term',
                                                 default=''),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('pyrax_sale.sale_delivery_term', self.sale_delivery_term)
