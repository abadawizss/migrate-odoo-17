# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_unlink_order(self):
        """ Unlink current move from sale order with this move is connected
        """
        sale_orders = self.env['sale.order'].search([('invoice_ids', 'in', self.ids)])
        for order in sale_orders:
            order.order_line.write({'invoice_lines': [(3, mv_line.id)
                                                      for mv_line in self.invoice_line_ids]})
            self.write({'invoice_origin': '', 'exporter_ref': ''})
        return True


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def get_sale_tax_grouping_key(self, invoice_tax_val):
        self.ensure_one()
        return str(invoice_tax_val['tax_id']) + '-' + str(invoice_tax_val['account_id'])