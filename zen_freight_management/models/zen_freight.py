from odoo import api, fields, models, _


class ZenFreightSaleOrderZen(models.Model):
    _inherit = "sale.order"

    freight_charges = fields.Monetary(string='Freight Charges', readonly=True, store=True, compute='_amount_all')

    # @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'freight_charges')
    # def _compute_amounts(self):
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type)
    #         if order.company_id.tax_calculation_rounding_method == 'round_globally':
    #             tax_results = self.env['account.tax']._compute_taxes([
    #                 line._convert_to_tax_base_line_dict()
    #                 for line in order_lines
    #             ])
    #             totals = tax_results['totals']
    #             amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
    #             amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
    #             # Round amount_tax to the nearest whole number
    #             amount_tax = round(amount_tax, 0)  # Rounding to 0 decimal places

    #             #FREIGHT CHARGE
    #             totals[order.currency_id]['freight_charges'] = totals.get(order.currency_id, {}).get('freight_charges', 0.0)
    #             # Calculate FREIGHT CHARGE and add it to totals
    #             if amount_untaxed > 200000:
    #                 totals[order.currency_id]['freight_charges'] = 0.0  # Pengiriman gratis jika pesanan melebihi 2 lakhs
    #             elif 31000 <= amount_untaxed <= 200000:
    #                 freight_charges = max(amount_untaxed * 0.0113, 350)
    #                 freight_charges = round(freight_charges, 0)
    #                 totals[order.currency_id]['freight_charges'] = freight_charges
    #             else:
    #                 totals[order.currency_id]['freight_charges'] = 0.0  # Pengiriman gratis jika pesanan kurang dari 31000
    #         else:
    #             amount_untaxed = sum(order_lines.mapped('price_subtotal'))
    #             amount_tax = sum(order_lines.mapped('price_tax'))

    #             #FREIGHT CHARGE
    #             totals[order.currency_id]['freight_charges'] = totals.get(order.currency_id, {}).get('freight_charges', 0.0)
    #             # Calculate FREIGHT CHARGE and add it to totals
    #             if amount_untaxed > 200000:
    #                 totals[order.currency_id]['freight_charges'] = 0.0  # Pengiriman gratis jika pesanan melebihi 2 lakhs
    #             elif 31000 <= amount_untaxed <= 200000:
    #                 freight_charges = max(amount_untaxed * 0.0113, 350)
    #                 freight_charges = round(freight_charges, 0)
    #                 totals[order.currency_id]['freight_charges'] = freight_charges
    #             else:
    #                 totals[order.currency_id]['freight_charges'] = 0.0  # Pengiriman gratis jika pesanan kurang dari 31000

    #         # Format amount_tax as a string with two trailing zeros
    #         amount_tax_str = '{:.2f}'.format(amount_tax)

    #         order.amount_untaxed = amount_untaxed
    #         order.freight_charges = totals[order.currency_id].get('freight_charges', 0.0)
    #         order.amount_tax = float(amount_tax_str)  # Convert the formatted string back to float
    #         order.amount_total = order.amount_untaxed + order.amount_tax

    @api.depends('order_line.price_total', 'freight_charges')
    def _amount_all(self):
        """ Compute the total amounts of the SO. """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if amount_untaxed > 200000:
                freight_charges = 0.0
            elif 31000 <= amount_untaxed <= 200000:
                freight_charges = max(amount_untaxed * 0.0113, 350)
                freight_charges = round(freight_charges, 0)
            else:
                freight_charges = 0.0
            order.update({
                'freight_charges': freight_charges
            })


class InheritSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # """Method for posting freight charges sale order to invoice if down payment"""
    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'type': 'out_invoice',
            'invoice_origin': order.name,
            'freight_charges': order.freight_charges,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'invoice_payment_ref': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        return invoice_vals


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    freight_charges = fields.Monetary(string='Freight Charges', readonly=False)

    # """Method for compute amount total with addition of freight charges"""
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()
            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===
                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_total = move.amount_total + self.freight_charges
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_residual = move.amount_residual + self.freight_charges
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'