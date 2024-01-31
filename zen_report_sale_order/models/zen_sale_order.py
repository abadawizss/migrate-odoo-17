from odoo import api, fields, models, tools, _


class SaleOrderZen(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')
    def _compute_amounts(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
                
                # Round amount_tax to the nearest whole number
                amount_tax = round(amount_tax, 0)  # Rounding to 0 decimal places
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                amount_tax = sum(order_lines.mapped('price_tax'))

            # Format amount_tax as a string with two trailing zeros
            amount_tax_str = '{:.2f}'.format(amount_tax)

            order.amount_untaxed = amount_untaxed
            order.amount_tax = float(amount_tax_str)  # Convert the formatted string back to float
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            tax_totals_dict = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )
            if tax_totals_dict['subtotals']:
                if 'formatted_amount' in tax_totals_dict['subtotals'][0]:
                    formatted_amount = tax_totals_dict['subtotals'][0]['formatted_amount']
                    parts = formatted_amount.split('.')
                    if len(parts) == 2:
                        formatted_amount = f"{parts[0]}"  
                    tax_totals_dict['subtotals'][0]['formatted_amount'] = formatted_amount

                for taxes in tax_totals_dict['groups_by_subtotal']['Untaxed Amount']:
                    tax_totals = round(taxes['tax_group_amount'],0)
                    taxes['tax_group_amount'] = tax_totals
                    currency = order.currency_id or order.company_id.currency_id
                    currency_symbol = currency.symbol  
                    formatted_tax_group = '{currency_symbol}\xa0{:,}'.format(tax_totals, currency_symbol=currency_symbol)
                    tax_group = formatted_tax_group.split('.')
                    if len(tax_group) == 2:
                        formatted_tax_group = f"{tax_group[0]}"
                    taxes['formatted_tax_group_amount'] = formatted_tax_group

                for base_amount_tax in tax_totals_dict['groups_by_subtotal']['Untaxed Amount']:
                    formatted_tax_group_base_amount = base_amount_tax['formatted_tax_group_base_amount']
                    base_tax_group = formatted_tax_group_base_amount.split('.')
                    if len(base_tax_group) == 2:
                        formatted_tax_group_base_amount = f"{base_tax_group[0]}"
                    base_amount_tax['formatted_tax_group_base_amount'] = formatted_tax_group_base_amount

                if 'formatted_amount_total' in tax_totals_dict:
                    formatted_amount_total = tax_totals_dict['formatted_amount_total']
                    amount_total = formatted_amount_total.split('.')
                    if len(amount_total) == 2:
                        formatted_amount_total = f"{amount_total[0]}"  # Hapus dua digit terakhir
                    tax_totals_dict['formatted_amount_total'] = formatted_amount_total
            order.tax_totals = tax_totals_dict
    # @api.model
    # def get_page_count(self, sale_order_ids):
    #     # Cari template HTML dengan nama yang Anda inginkan
    #     sale_order = self.env['sale.order'].browse(sale_order_ids)

    #     # Calculate the number of pages (assuming 20 lines per page)
    #     lines_per_page = 5
    #     total_lines = len(sale_order.order_line)
    #     total_pages = total_lines // lines_per_page + (total_lines % lines_per_page > 0)

    #     return total_pages

class ZenSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    hsn_id = fields.Many2one('master.hsn', string='HSN/SAC Code', related='product_id.hsn_id')