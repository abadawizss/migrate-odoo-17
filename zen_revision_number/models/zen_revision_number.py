from datetime import datetime
import json
import re
from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    revision_number = fields.Integer('Revision Number')
    show_revision_number = fields.Boolean('Show Revision Number', compute='_show_revision_number')
    revision_date = fields.Date('Revision Date')
    
    def _show_revision_number(self):
        for record in self:
            if record.revision_number == 0:
                record.show_revision_number = False
            elif record.revision_number > 0:
                record.show_revision_number = True

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_revision_number(self, order):
        if not order.revision_number:
            return 1
        else:
            rev = order.revision_number + 1
            return rev
    
    def action_send_mail(self):
        res = super(MailComposeMessage, self).action_send_mail()
        if res and self.env.context.get('mark_so_as_sent'):
            active_model = self.env.context.get('default_model')
            active_id = self.env.context.get('default_res_ids')
            if active_model == 'sale.order' and active_id:
                order = self.env[active_model].browse(active_id)
                order.revision_number = self.get_revision_number(order)
                order.update({'revision_number': order.revision_number,'revision_date':fields.Date.today()})
        return res