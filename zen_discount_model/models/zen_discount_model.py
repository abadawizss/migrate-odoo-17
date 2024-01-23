# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ZenDiscount(models.Model):
    _name = 'zen.discount'
    _description = 'Discount Model'


    group_id = fields.Many2one('zen.discount.group', string='Discount Group')
    minimum_qty = fields.Float('Minimum Quantity')
    maximum_qty = fields.Float('Maximum Quantity')
    maximum_discount_percentage = fields.Float('Maximum Discount Percentage')


class ZenDiscountGroup(models.Model):
    _name = 'zen.discount.group'
    _description = 'Discount Group'
    _rec_name = 'name'

    name = fields.Char('Group Name')
    discount_group_ids = fields.Many2many('product.product','groups_product_rel', string='Product')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for line in self.order_line:
            line.onchange_product_id()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def onchange_product_id(self):
        if self.product_id and self.order_id.partner_id:
            contact_type = self.order_id.partner_id.contact_type
            product_qty = self.product_uom_qty
            applicable_discount = self.get_applicable_discount(self.product_id, contact_type, product_qty)
            self.discount = applicable_discount

    def get_applicable_discount(self, product, contact_type, quantity):
        discounts = 0.0
        if contact_type == 'end_user':
            percentage_discount_end_user = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.percentage_discount')
            if percentage_discount_end_user:
                discounts = float(percentage_discount_end_user)
        elif contact_type == 'dealer':
            discount_group = self.env['zen.discount.group'].sudo().search([('discount_group_ids','=',product.id)])
            if discount_group:
                discounts = self.env['zen.discount'].sudo().search([
                ('group_id', '=', discount_group.id),
                ('minimum_qty', '<=', quantity),
                ('maximum_qty', '>=', quantity),
            ], order='maximum_discount_percentage DESC', limit=1).maximum_discount_percentage

        return discounts if discounts else 0.0