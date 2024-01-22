# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class AccountMoveDistributedLine(models.Model):
    # _inherit = 'account.move.line'
    _name = "account.move.distributed.line"
    _description = "Distributed Lines"

    is_distributed_line = fields.Boolean(string="IS Distributed Line")
    distributed_move_id = fields.Many2one('account.move', string="Distributed Move")
    # distributed_move_id = fields.Many2one('account.move', string="Distributed Move", auto_join=True, ondelete="cascade", index=True)
    invoice_line_id = fields.Many2one('account.move.line', string="Invoice Line Reference")
    sale_line_ids = fields.Many2many(
        'sale.order.line',
        'sale_order_line_invoice_distributed_rel',
        'invoice_line_id', 'order_line_id',
        string='Sales Order Lines', readonly=True, copy=False)
    hsn_code = fields.Char(string="HSN Code")
    price_unit = fields.Float(string='Unit Price', digits=(6, 6))
    price_unit_signed = fields.Float(string="Distributed Unit price in company currency", compute='_compute_distributed_price', store=True, readonly=True, digits=(6, 6))
    distributed_price_subtotal = fields.Float(string='Distributed Subtotal', compute='_compute_distributed_price', store=True, readonly=True, digits=(4, 4))
    distribute_total_signed = fields.Float(string="Distributed Total", compute='_compute_distributed_price', store=True, readonly=True, digits=(4, 4))
    distributed_asset_ids = fields.Many2many('account.asset', 'distributed_account_asset_rel', 'distributed_line_id', 'asset_id', string='Assets')

    @api.depends('price_unit')
    def _compute_distributed_price(self):
        pass
    #     for line in self:
    #         price_unit_signed = line.price_unit
    #         price_subtotal = total_signed = (line.quantity * line.price_unit)
    #         line.distributed_price_subtotal = price_subtotal
    #         if line.currency_id and line.currency_id != line.distributed_move_id.company_id.currency_id:
    #             # Multi-currencies.
    #             total_signed = line.currency_id._convert(
    #                 total_signed, line.distributed_move_id.company_id.currency_id, \
    #                 line.distributed_move_id.company_id, line.distributed_move_id.date)
    #         line.price_unit_signed = total_signed / line.quantity
    #         line.distribute_total_signed = total_signed
