from odoo import models, fields, api
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError


class ConfigurationReminderCRM(models.TransientModel):
    _inherit = 'res.config.settings'

    
    activate_approval_payment_term = fields.Boolean('Payment Terms Approval Exclusion', config_parameter="zen_sale_order.activate_approval_payment_term")
    user_approval_payment_term = fields.Many2many('hr.employee', 'res_config_users_approval_payment_term',string='Payment Terms Approval Authorities', compute="_compute_approval_authority_payment_term", inverse="_inverse_approval_authority_payment_term")
    user_approval_list_payment_term = fields.Char('Payment Terms Approval Authorities', config_parameter="zen_sale_order.user_approval_list_payment_term")
    minimum_approval_payment_term = fields.Integer('Minimum Approvals Required', config_parameter="zen_sale_order.minimum_approval_payment_term")
    payment_term = fields.Many2many('account.payment.term', 'res_config_type_payment_term',string='Payment Terms', compute="_compute_payment_term", inverse="_inverse_payment_term")
    payment_term_list= fields.Char('Payment Terms', config_parameter="zen_sale_order.payment_term_list")


    @api.depends('user_approval_list_payment_term')
    def _compute_approval_authority_payment_term(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.user_approval_list_payment_term:
                names = setting.user_approval_list_payment_term.split(',')
                employee_ids = [int(id_str) for id_str in names if id_str.strip().isdigit()]
                setting.user_approval_payment_term = self.env['hr.employee'].browse(employee_ids)
            else:
                setting.user_approval_payment_term = None
    
    def _inverse_approval_authority_payment_term(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.user_approval_payment_term:
                setting.user_approval_list_payment_term = ','.join(str(e.id) for e in self.user_approval_payment_term)
            else:
                setting.user_approval_list_payment_term = ''
    
    @api.constrains('user_approval_list_payment_term')
    def _check_user_approval_constraints(self):
        for setting in self:
            if setting.minimum_approval_payment_term and setting.user_approval_payment_term:
                if len(setting.user_approval_payment_term) > setting.minimum_approval_payment_term:
                    raise ValidationError("You can select at most {} approval authorities.".format(setting.minimum_approval_payment_term))
    
    @api.depends('payment_term_list')
    def _compute_payment_term(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.payment_term_list:
                names = setting.payment_term_list.split(',')
                payment_terms_ids = [int(id_str) for id_str in names if id_str.strip().isdigit()]
                setting.payment_term = self.env['account.payment.term'].browse(payment_terms_ids)
            else:
                setting.payment_term = None
    
    def _inverse_payment_term(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.payment_term:
                setting.payment_term_list = ','.join(str(e.id) for e in setting.payment_term)
            else:
                setting.payment_term_list = ''
