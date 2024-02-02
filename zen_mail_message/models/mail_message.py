from odoo import models, fields


class ConfigChatter(models.TransientModel):
    _inherit = 'res.config.settings'

    active_chatter_in_crm = fields.Boolean(string='Enabled Chatter CC in Module CRM', config_parameter="zen_mail_message.active_chatter_in_crm")
    active_chatter_in_sale = fields.Boolean(string='Enabled Chatter CC in Module Sale', config_parameter="zen_mail_message.active_chatter_in_sale")
    active_chatter_in_purchase = fields.Boolean(string='Enabled Chatter CC in Module Purchase', config_parameter="zen_mail_message.active_chatter_in_purchase")