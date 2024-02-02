# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools.mail import is_html_empty


class SaleOrderMentionReasonExtraDiscount(models.TransientModel):
    _name = 'sale.order.mention.reason'
    _description = 'Get Mention Reason'

    remarks = fields.Html(
        'Reason Extra discount and Payment Term', sanitize=True
    )

    def action_mention(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if not is_html_empty(self.remarks):
            sale_order._track_set_log_message(
                '<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>' % (
                    _('Reason Extra discount , Payment Term, Freight Charges'),
                    self.remarks
                )
            )
        
        for rec in sale_order.exception_ids.filtered(lambda x: x.request_date == False):
            date_timestamp = fields.Datetime.now()
            rec.sudo().write({'request_date': date_timestamp})
            
        res = sale_order.sudo().write({'state': 'waiting_approved'})
        return res

class RejectException(models.TransientModel):
    _name = 'reject.exception'
    _description = 'Reject Exception'

    remarks = fields.Html(
        'Reason Reject Exceptions', sanitize=True
    )

    def action_reject(self):
        self.ensure_one()
        date = fields.Datetime.now()
        exception_so_ids = self.env['zen.sale.order.exception'].browse(self.env.context.get('active_ids'))
        if not is_html_empty(self.remarks):
            exception_so_ids.order_id._track_set_log_message(
                '<div style="margin-bottom: 4px;"><p><b>%s:</b></p><p><b>Exception : %s  Normal %s Current %s Amount %s</b></p><br /> <p><b>Reason : <span>%s</span></b></p></div>' % (
                    _('Reason Reject Exceptions'),
                    exception_so_ids.exception_name,
                    exception_so_ids.normal,
                    exception_so_ids.current,
                    exception_so_ids.amount,
                    self.remarks
                )
            )
        
        res = exception_so_ids.sudo().write({'status': 'reject','approver_action_date': date})
        return res
        