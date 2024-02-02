from odoo import models, fields, api
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError


class ConfigurationReminderCRM(models.TransientModel):
    _inherit = 'res.config.settings'

    #CRM REMINDER
    activate_approval_discount = fields.Boolean('Activate Approval Discount', config_parameter="zen_sale_order.activate_approval_discount")
    percentage_discount = fields.Float('Percentage', config_parameter="zen_sale_order.percentage_discount", default=5)
    user_approval = fields.Many2many('hr.employee', 'res_config_users_approval_discount',string='Approval Authority', compute="_compute_approval_authority", inverse="_inverse_approval_authority")
    user_approval_list = fields.Char('Approval Authority', config_parameter="zen_sale_order.user_approval_list")
    minimum_approval = fields.Integer('Minimum Approvals Required', config_parameter="zen_sale_order.minimum_approval")

    @api.depends('user_approval_list')
    def _compute_approval_authority(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.user_approval_list:
                names = setting.user_approval_list.split(',')
                employee_ids = [int(id_str) for id_str in names if id_str.strip().isdigit()]
                setting.user_approval = self.env['hr.employee'].browse(employee_ids)
            else:
                setting.user_approval = None
    
    def _inverse_approval_authority(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.user_approval:
                setting.user_approval_list = ','.join(str(e.id) for e in self.user_approval)
            else:
                setting.user_approval_list = ''
    
    @api.constrains('user_approval')
    def _check_user_approval_constraints(self):
        for setting in self:
            if setting.minimum_approval and setting.user_approval:
                if len(setting.user_approval) > setting.minimum_approval:
                    raise ValidationError("You can select at most {} approval authorities.".format(setting.minimum_approval))