from odoo import api, fields, models, _


class ZenFreightSaleOrderZen(models.Model):
    _inherit = "sale.order"

    freight_charges = fields.Monetary(string='Freight Charges', readonly=True, store=True, compute='_amount_all')
    exclude = fields.Boolean('Exclude Freight', default=False)

    @api.depends('order_line.price_total', 'freight_charges', 'exclude')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            freight_charges = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if amount_untaxed != 0:
                active_approval_freight= self.env['ir.config_parameter'].sudo().get_param('zen_freight_management.activate_freight_charges')
                if active_approval_freight:
                    if not order.exclude:
                        if amount_untaxed >= 200000:
                            freight_charges = 0.0
                        elif amount_untaxed <= 200000:
                            freight_charges = max(amount_untaxed * 0.0113, 400)
                            freight_charges = round(freight_charges, 0)
                        else:
                            freight_charges = 0.0
                    else:
                        freight_charges = 0.0
            order.update({
                'freight_charges': freight_charges,
                'amount_untaxed': amount_untaxed + freight_charges,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
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


class ConfigurationFreight(models.TransientModel):
    _inherit = 'res.config.settings'

    activate_freight_charges = fields.Boolean('Activate Approval Freight Charges', config_parameter="zen_freight_management.activate_freight_charges")
    user_approval_freight_charges = fields.Many2many('hr.employee', 'res_config_users_approval_freight_charges',string='Payment Terms Approval Authorities', compute="_compute_approval_authority_freight_charges", inverse="_inverse_approval_authority_freight_charges")
    user_approval_list_freight_charges = fields.Char('Payment Terms Approval Authorities', config_parameter="zen_freight_management.user_approval_list_freight_charges")
    
    @api.depends('user_approval_list_freight_charges')
    def _compute_approval_authority_freight_charges(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.user_approval_list_freight_charges:
                names = setting.user_approval_list_freight_charges.split(',')
                employee_ids = [int(id_str) for id_str in names if id_str.strip().isdigit()]
                setting.user_approval_freight_charges = self.env['hr.employee'].browse(employee_ids)
            else:
                setting.user_approval_freight_charges = None
    
    def _inverse_approval_authority_freight_charges(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.user_approval_freight_charges:
                setting.user_approval_list_freight_charges = ','.join(str(e.id) for e in self.user_approval)
            else:
                setting.user_approval_list_freight_charges = ''