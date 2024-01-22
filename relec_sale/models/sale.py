# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import float_round

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_tax_line_vals(self, line, tax):
        """ Prepare values to create an sale.order.tax line

        The line parameter is an sale.order.line, and the
        tax parameter is the output of sale.order.tax.compute_all().
        """
        tax_id = self.env['account.tax'].browse(tax['id'])
        vals = {
            'order_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'description': tax_id.description,
            'manual': False,
            'sequence': tax['sequence'],
            'account_id': tax['account_id'] or tax['refund_account_id'],
        }

        return vals

    def get_taxes_values(self):
        tax_grouped = {}
        final_tax_grouped = {}
        currency_id = self.currency_id or self.env.company.currency_id

        #  Rounding Method: How total tax amount is computed
        prec = currency_id.decimal_places
        round_tax = False if self.env.company.tax_calculation_rounding_method == 'round_globally' else True
        if not round_tax:
            prec += 5

        for line in self.order_line:
            if not line.product_id:
                continue
            price_unit = line.price_unit * \
                (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id._origin.compute_all(price_unit,
                                                    quantity=line.product_uom_qty,
                                                    currency=currency_id,
                                                    product=line.product_id,
                                                    partner=self.partner_id)['taxes']
            if taxes and len(taxes) == 1:
                continue
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(
                    tax['id']).get_sale_tax_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = float_round(val['base'], prec)
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += float_round(val['base'], prec)
        for tax in tax_grouped:
            if 'SGST' in tax_grouped[tax].get('name'):
                key = 'SGST'
            elif 'CGST' in tax_grouped[tax].get('name'):
                key = 'CGST'
            if key not in final_tax_grouped:
                final_tax_grouped[key] = tax_grouped[tax]
                final_tax_grouped[key]['base'] = float_round(tax_grouped[tax]['base'], prec)
            else:
                final_tax_grouped[key]['amount'] += tax_grouped[tax]['amount']
                final_tax_grouped[key]['base'] += float_round(tax_grouped[tax]['base'], prec)
        return final_tax_grouped

    @api.model
    def default_get(self, fields):
        vals = super(SaleOrder, self).default_get(fields)
        sale_delivery_term = self.env['ir.config_parameter'].sudo(
        ).get_param('pyrax_sale.sale_delivery_term')
        if sale_delivery_term:
            vals['delivery_payment_terms'] = sale_delivery_term

        return vals

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for order in self:
            if order.currency_id:
                order.amount_total_words = order.currency_id.amount_to_text(
                    order.amount_total)

    @api.depends('name', 'date_order')
    def _compute_export_ref(self):
        for order in self:
            if not order.name or not order.date_order:
                order.exporter_ref = ''
                continue
            order.exporter_ref = order.name + '-' + \
                datetime.strftime(order.date_order.date(), '%d-%m-%Y')

    amount_total_words = fields.Char(
        "Total (In Words)", compute="_compute_amount_total_words")
    exporter_ref = fields.Char("Exporter's Ref", compute=_compute_export_ref,
                               store=True, copy=False)
    # Transport
    transport = fields.Char(string="Transport")
    carrier_id = fields.Many2one('delivery.carrier', 'Carriage By')
    pre_carrier_receipt_place = fields.Char(
        string="Place of Receipt by Pre Carrier")
    origin_country_id = fields.Many2one('res.country',
                                        string='Country of Origin of Goods')
# default=lambda x: x.env.company.country_id.id)
    port_loading = fields.Char(string="Port of Loading")
    port_discharge = fields.Char(string="Port of Discharge")
    delivery_payment_terms = fields.Text(string="Terms of Delivery & Payment")
    # Bank
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account',
                                      help="Bank account that was used in this transaction.")
    corr_bank_account_id = fields.Many2one(
        'res.partner.bank', string='Correspondent Bank Account')
    additional_bank_details = fields.Char()
    print_stamp = fields.Boolean('Print Stamp?')
    print_signature = fields.Boolean('Print Signature?')

    # def action_quotation_send(self):
    #     ''' Override to pass PRO-FORMA email template and report
    #     if Send By PRO-FORMA Invoice '''
    #     response = super(SaleOrder, self).action_quotation_send()
    #     self.ensure_one()
    #     if self.env.context.get('proforma', False):
    #         ctx = response.get('context', {})
    #         template_id = self.env['ir.model.data'].xmlid_to_res_id('relec_sale.email_template_edi_sale_proforma',
    #                                                                 raise_if_not_found=False)
    #         lang = self.env.context.get('lang')
    #         template = self.env['mail.template'].browse(template_id)
    #         if template.lang:
    #             lang = template._render_template(
    #                 template.lang, 'sale.order', self.ids[0])
    #         ctx.update({
    #             'default_use_template': bool(template_id),
    #             'default_template_id': template_id,
    #             'proforma': self.env.context.get('proforma', False),
    #             'model_description': self.with_context(lang=lang).type_name,
    #         })
    #         response.update({'context': ctx})
    #     return response

    def _prepare_invoice(self):
        """ Pass Transport and bank fields value to invoice """
        vals = super(SaleOrder, self)._prepare_invoice()
        vals.update({'transport': self.transport,
                     'pre_carrier_receipt_place': self.pre_carrier_receipt_place,
                     'port_loading': self.port_loading,
                     'port_discharge': self.port_discharge,
                     'carrier_id': self.carrier_id and self.carrier_id.id,
                     'bank_account_id': self.bank_account_id.id,
                     'corr_bank_account_id': self.corr_bank_account_id.id,
                     'additional_bank_details': self.additional_bank_details,
                     'exporter_ref': self.exporter_ref,
                     'delivery_payment_terms': self.delivery_payment_terms,
                     'print_stamp': self.print_stamp,
                     'print_signature': self.print_signature})
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    use_date = fields.Datetime(string="Best Before Date")

    @api.onchange("lot_id")
    def lot_id_change(self):
        if not self.lot_id:
            self.use_date = False
            return
        self.use_date = self.lot_id.use_date

    # def _prepare_invoice_line(self):
    #     """
    #         override method to pass expiry date of product in invoice line.
    #     """
    #     res = super(SaleOrderLine, self)._prepare_invoice_line()
    #     res.update({'use_date': self.use_date})
    #     return res

class StockProductLot(models.Model):
    _inherit = 'stock.lot'
    # _inherit = 'stock.production.lot'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(StockProductLot, self)._name_search(name, args, operator, limit, name_get_uid)
        context = dict(self._context) or {}
        if context.get('product_id', False) and context.get('warehouse_id', False):
            warehouse_id = self.env['stock.warehouse'].browse([context['warehouse_id']])
            quants = self.env["stock.quant"].read_group(
                [("product_id", "=", context['product_id']),
                 ("location_id", "child_of", warehouse_id.lot_stock_id.id),
                 ("quantity", ">", 0), ("lot_id", "!=", False)], ["lot_id"], "lot_id",)
            available_lot_ids = [quant["lot_id"][0] for quant in quants]
            return models.lazy_name_get(self.browse(available_lot_ids).with_user(name_get_uid))
        return res
