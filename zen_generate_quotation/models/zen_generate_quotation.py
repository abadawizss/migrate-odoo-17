
from datetime import datetime
import json
import re
from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                # Compute the relevant year based on the quotation_date
                if vals.get('date_order'):
                    date_order_str = vals['date_order'].split()[0]  # Extract date part only
                    date_order = datetime.strptime(date_order_str, "%Y-%m-%d")
                    year = date_order.year
                    if date_order.month >= 4:
                        this_date =str(year)[2:]
                        next_date = str(year + 1)[2:]
                        relevant_year = this_date +'-'+next_date
                    else:
                        this_date = str(year)[2:]
                        before_date = str(year - 1)[2:]
                        relevant_year = before_date +'-'+ this_date
                    # Get the last used sequential number for the relevant financial year
                    last_seq_number_rec = self.env['sale.order'].sudo().search([
                        ('name', 'like', 'ADIN/' + relevant_year + '/%')
                    ], order='id desc', limit=1)

                    if last_seq_number_rec and last_seq_number_rec.name:
                        last_seq_number_match = re.search(r'\d+$', last_seq_number_rec.name)
                        if last_seq_number_match:
                            last_seq_number = int(last_seq_number_match.group())
                            sequence_number = last_seq_number + 1
                        else:
                            sequence_number = 1
                    else:
                        sequence_number = 1

                    # Add the prefix "ADIN/" and relevant_year before the sequence number
                    vals['name'] = 'ADIN/' + relevant_year + '/' + str(sequence_number).zfill(4)
                if not vals.get('date_order'):
                    date_order = datetime.now()
                    date_order_str = str(date_order).split()[0]  # Extract date part only
                    date_order = datetime.strptime(date_order_str, "%Y-%m-%d")
                    year = date_order.year
                    if date_order.month >= 4:
                        this_date =str(year)[2:]
                        next_date = str(year + 1)[2:]
                        relevant_year = this_date +'-'+next_date
                    else:
                        this_date = str(year)[2:]
                        before_date = str(year - 1)[2:]
                        relevant_year = before_date +'-'+ this_date
                    # Get the last used sequential number for the relevant financial year
                    last_seq_number_rec = self.env['sale.order'].sudo().search([
                        ('name', 'like', 'ADIN/' + relevant_year + '/%')
                    ], order='id desc', limit=1)

                    if last_seq_number_rec and last_seq_number_rec.name:
                        last_seq_number_match = re.search(r'\d+$', last_seq_number_rec.name)
                        if last_seq_number_match:
                            last_seq_number = int(last_seq_number_match.group())
                            sequence_number = last_seq_number + 1
                        else:
                            sequence_number = 1
                    else:
                        sequence_number = 1

                    # Add the prefix "ADIN/" and relevant_year before the sequence number
                    vals['name'] = 'ADIN/' + relevant_year + '/' + str(sequence_number).zfill(4) 
            return super(SaleOrder, self).create(vals)
    