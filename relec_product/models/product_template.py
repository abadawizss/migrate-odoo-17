# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    free_sale_certificate = fields.Char(string="Free Sale Certificate")
    has_product_drawback = fields.Boolean(string="Has Product Drawbacks")
    has_product_dangerous_goods = fields.Boolean(
        string="Has Product Dangerous Goods")
    gross_weight = fields.Float(string="Gross Weight")
