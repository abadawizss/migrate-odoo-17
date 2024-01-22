# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class AccountMove(models.Model):
    _inherit = "account.move"

#     def _get_default_report_note(self):
#         return """Avail Merchant Export Intensive Scheme"""

    bags_count = fields.Char(string="No. of Bags/Boxes")
    transport = fields.Char(string="Transport")
    pre_carrier_receipt_place = fields.Char(string="Place of Receipt by Pre Carrier")
    port_loading = fields.Char(string="Port of Loading")
    port_discharge = fields.Char(string="Port of Discharge")
    dispatch_document_no = fields.Char(string="Dispatch Document No")
    dispatch_through = fields.Char(string="Despatched Through")
    delivery_note = fields.Char(string="Delivery Note")
    delivery_note_date = fields.Date(string="Delivery Note Date")
    delivery_payment_terms = fields.Text(string="Terms of Delivery & Payment")
    carrier_id = fields.Many2one('delivery.carrier', 'Carriage By')
    exporter_ref = fields.Char("Exporter's Ref")
    tax_inv_base = fields.Selection([('on_pay', 'ON PAYMENT OF IGST'), ('without_pay', 'WITHOUT PAYMENT OF IGST')], default='without_pay', string='Based On')
    tax_inv_note = fields.Text('Tax Invoice Note', compute="_compute_tax_inv_note", store=True, readonly=False)
    buyer_order_no = fields.Char(string="Buyer Order No")

    # Bank
    bank_account_id = fields.Many2one('res.partner.bank', string='Company Bank Account', help="Bank account that was used in this transaction.")
    corr_bank_account_id = fields.Many2one('res.partner.bank', string='Correspondent Bank Account')
    additional_bank_details = fields.Char()
    # report_note = fields.Text(string="Report Note", default=_get_default_report_note)
    print_stamp = fields.Boolean('Print Stamp?')
    print_signature = fields.Boolean('Print Signature?')
    distributed_line_ids = fields.One2many('account.move.distributed.line', 'distributed_move_id', string="Distributed Lines", domain=[('is_distributed_line', '=', True)], copy=False, states={'draft': [('readonly', False)]})
    integrated_tax_ids = fields.One2many('account.integrated.tax', 'move_id', string="Integrated Taxes", compute='compute_integrated_taxes', store=True,)

    @api.depends('tax_inv_base')
    def _compute_tax_inv_note(self):
        for move in self:
            if move.tax_inv_base and move.tax_inv_base == 'without_pay':
                move.tax_inv_note = "(SUPPLY MEANT FOR EXPORT/SUPPLY TO SEZ UNIT" \
                                    " OR SEZ DEVELOPER FOR AUTHORISED OPERATIONS" \
                                    " UNDER BOND OR LETTER OF UNDERTAKING WITHOUT PAYMENT OF IGST)"
            elif move.tax_inv_base:
                move.tax_inv_note = "(SUPPLY MEANT FOR EXPORT/SUPPLY TO SEZ UNIT" \
                                    " OR SEZ DEVELOPER FOR AUTHORISED OPERATIONS ON PAYMENT OF IGST)"
            else:
                move.tax_inv_note = ""

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'tax_inv_base' in vals:
            for move in self:
                move.compute_integrated_taxes()
        return res

    def get_hsn_code_values(self):
        self.integrated_tax_ids.unlink()
        hsn_grouped = {}
        for line in self.distributed_line_ids:
            key = line.hsn_code
            if key:
                if key not in hsn_grouped:
                    tax_id = False
                    if self.tax_inv_base == 'on_pay':
                        tax_id = line.product_id.taxes_id and line.product_id.taxes_id[0].id or False
                    hsn_grouped[key] = {'name': key,
                                        'taxable_amount': line.distribute_total_signed,
                                        'move_id': self.id,
                                        'tax_id': tax_id}
                else:
                    hsn_grouped[key]['taxable_amount'] += line.distribute_total_signed
        return hsn_grouped

    @api.depends('distributed_line_ids')
    def compute_integrated_taxes(self):
        for move in self:
            integrated_tax_lines = self.env['account.integrated.tax']
            hsn_grouped = move.get_hsn_code_values()
            for hsn_code in hsn_grouped.values():
                integrated_tax_lines |= integrated_tax_lines.create(hsn_code)
            move.integrated_tax_ids = integrated_tax_lines

    # def button_cancel(self):
    #     res = super(AccountMove, self).button_cancel()
        # self.mapped('distributed_line_ids').remove_move_reconcile()
        # self.distributed_line_ids.unlink()
        # return res

    # def button_draft(self):
    #     res = super(AccountMove, self).button_draft()
        # self.mapped('distributed_line_ids').remove_move_reconcile()
        # self.distributed_line_ids.unlink()
        # return res

    # def action_post(self):
    #     service_product_ids = self.invoice_line_ids.filtered(lambda l: l.product_id.type == 'service')
    #     if service_product_ids:
    #         for move in self:
    #             if not move.distributed_line_ids:
    #                 move.compute_distributed_lines()
    #     return super(AccountMove, self).action_post()

    def compute_distributed_lines(self):
        self.mapped('distributed_line_ids').remove_move_reconcile()
        self.distributed_line_ids.unlink()
        distributed_lines = self.env['account.move.distributed.line']
        service_product_ids = self.invoice_line_ids.filtered(lambda l: l.product_id.type == 'service')
        # if not service_product_ids:
        #     return distributed_lines
        invoice_line_ids = self.invoice_line_ids.filtered(lambda l: l.product_id.type != 'service').sorted(key=lambda l: (-l.sequence, l.date, l.move_name, -l.id), reverse=True)
        all_product_dwb_yes = all(line.product_id.has_product_drawback for line in invoice_line_ids)
        all_product_dwb_no = all(not line.product_id.has_product_drawback for line in invoice_line_ids)
        service_charges = sum(service_product_ids.mapped('price_subtotal')) or 0.00
        product_charges = sum(invoice_line_ids.mapped('price_subtotal')) or 0.00
        # if not service_charges and not product_charges:
        #     return distributed_lines
        if ((all_product_dwb_yes or all_product_dwb_no) and service_charges):
            for line in invoice_line_ids:
                price_unit = ((service_charges / product_charges) * line.price_unit) + line.price_unit
                name = line.product_id and line.product_id.name or line.name
                if line.product_id and line.product_id.free_sale_certificate:
                    name = line.product_id.free_sale_certificate + ' - ' + name
                vals = {'product_id': line.product_id.id,
                        'name': name,
                        'move_id': self.id,
                        'hsn_code': line.product_id.l10n_in_hsn_code,
                        'currency_id': line.currency_id.id,
                        'exclude_from_invoice_tab': True,
                        'account_id': line.account_id.id,
                        'distributed_move_id': self.id,
                        'invoice_line_id': line.id,
                        'quantity': line.quantity,
                        'price_unit': price_unit,
                        'product_uom_id': line.product_uom_id.id,
                        'display_type': line.display_type,
                        'is_distributed_line': True,
                        'discount': line.discount,
                        }
                distributed_lines |= distributed_lines.create(vals)
        else:
            # When All Products’ DWB are “Y” and “N”
            inv_lines_product_dwb_no = invoice_line_ids.filtered(lambda l: l.product_id and not l.product_id.has_product_drawback)
            inv_lines_product_dwb_yes = invoice_line_ids.filtered(lambda l: l.product_id and l.product_id.has_product_drawback)
            total_amt_adjusted = service_charges

            for line in inv_lines_product_dwb_no:
                if line.product_id.standard_price:
                    standard_price = self.company_currency_id._convert(line.product_id.standard_price, self.currency_id, self.company_id, self.date or fields.Date.today())
                    purchase_price = standard_price + (standard_price * 2 / 100)
                    total_purchase_price = purchase_price * line.quantity
                    total_amt_adjusted += line.price_subtotal - total_purchase_price
                else:
                    total_amt_adjusted += line.price_subtotal

            total_amt_dwb_yes = sum(ml.price_subtotal for ml in inv_lines_product_dwb_yes)
            for ml in invoice_line_ids:
                if ml.product_id.has_product_drawback:
                    price_unit = ((total_amt_adjusted / total_amt_dwb_yes) * ml.price_unit) + ml.price_unit
                else:
                    standard_price = self.company_currency_id._convert(ml.product_id.standard_price, self.currency_id, self.company_id, self.date or fields.Date.today())
                    price_unit = standard_price + (standard_price * 2 / 100)

                name = ml.product_id and ml.product_id.name or ml.name
                if ml.product_id and ml.product_id.free_sale_certificate:
                    name = ml.product_id.free_sale_certificate + ' - ' + name
                vals = {'product_id': ml.product_id.id,
                        'name': name,
                        'hsn_code': ml.product_id.l10n_in_hsn_code,
                        'quantity': ml.quantity,
                        'price_unit': price_unit,
                        'product_uom_id': ml.product_uom_id.id,
                        'display_type': ml.display_type,
                        'move_id': self.id,
                        'currency_id': ml.currency_id.id,
                        'exclude_from_invoice_tab': True,
                        'account_id': ml.account_id.id,
                        'distributed_move_id': self.id,
                        'invoice_line_id': ml.id,
                        'is_distributed_line': True,
                        'discount': ml.discount,
                        }
                distributed_lines |= distributed_lines.create(vals)

        return distributed_lines

    def _prepare_hsn_line_vals(self, line, tax):
        """ Prepare values to create a dict with line group by HSN code
        """
        vals = {
            'move_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_id': tax['account_id'] or False,
        }
        return vals

    def get_hsn_values(self):
        """ Domestic tax invoice report: prepare taxes line grouped by HSN code
        """
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids._origin.compute_all(price_unit,
                                                    quantity=line.quantity,
                                                    currency=self.currency_id,
                                                    product=line.product_id,
                                                    partner=self.partner_id)['taxes']
            tax_val = {}
            for tax in taxes:
                val = self._prepare_hsn_line_vals(line, tax)
                key = str(line.product_id.l10n_in_hsn_code)

                if key not in tax_val:
                    tax_val[key] = val
                    tax_val[key]['base'] = round_curr(val['base'])
                else:
                    tax_val[key]['amount'] += val['amount']
            for key, value in tax_val.items():
                if key not in tax_grouped:
                    tax_val[key]['name'] = ', '.join(map(lambda x: (x.description or x.name), line.tax_ids))
                    tax_val[key]['rate'] = sum([tax.amount for tax in line.tax_ids])
                    tax_grouped.update(tax_val)
                else:
                    tax_grouped[key]['base'] += round_curr(value['base'])
                    tax_grouped[key]['amount'] += round_curr(value['amount'])
        return tax_grouped


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    use_date = fields.Datetime(string="Best Before Date")