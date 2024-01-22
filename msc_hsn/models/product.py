# -*- coding: utf-8 -*-
###############################################################################
#
#    Meghsundar Private Limited(<https://www.meghsundar.com>).
#
###############################################################################
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hsn_id = fields.Many2one('master.hsn', string='HSN/SAC Code')

    @api.onchange('hsn_id')
    def onchange_hsn_id(self):
        self.l10n_in_hsn_description = self.hsn_id.description


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('hsn_id')
    def onchange_hsn_id(self):
        self.l10n_in_hsn_description = self.hsn_id.description