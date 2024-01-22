# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class AccountIntegratedTax(models.Model):
    _name = "account.integrated.tax"
    _description = "Integrated Taxes"

    move_id = fields.Many2one('account.move', string="Move", auto_join=True, ondelete="cascade", index=True)
    name = fields.Char(string="HSN Code", required=True)
    taxable_amount = fields.Float(string="Taxable Value")
    tax_id = fields.Many2one('account.tax', string="Rate")
    amount = fields.Float(string='Tax Amount', compute='_compute_amount', store=True, readonly=True)
    currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                  related='move_id.company_id.currency_id')

    @api.depends('tax_id', 'taxable_amount')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.taxable_amount, line.move_id.currency_id)
            line.update({
                'amount': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            })