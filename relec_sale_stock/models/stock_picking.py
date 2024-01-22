# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_no = fields.Char(string="Invoice No", compute='_compute_invoice_no_date', store=True)
    invoice_date = fields.Date(string="Invoice Date", compute='_compute_invoice_no_date', store=True)

    @api.depends('sale_id', 'sale_id.invoice_ids', 'sale_id.invoice_ids.state')
    def _compute_invoice_no_date(self):
        for picking in self:
            if not picking.sale_id or not picking.sale_id.invoice_ids:
                picking.invoice_no = False
                picking.invoice_date = False
                continue
            picking.invoice_no = picking.sale_id.invoice_ids[:1].name
            picking.invoice_date = picking.sale_id.invoice_ids[:1].invoice_date