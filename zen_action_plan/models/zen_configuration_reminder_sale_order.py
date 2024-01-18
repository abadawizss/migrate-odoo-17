from odoo import models, fields, api
from datetime import datetime, timedelta


class ConfigurationReminderSaleOrder(models.TransientModel):
    _inherit = 'res.config.settings'

    #QUOTATION REMINDER
    activate_reminder_quotation = fields.Boolean(string='Reminder Email Quotation', config_parameter="zen_action_plan.activate_reminder_quotation")
    interval_number_reminder_1_quo = fields.Integer('1st Reminder', config_parameter="zen_action_plan.interval_number_reminder_1_quo")
    interval_type_reminder_1_quo = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Interval Type 1', config_parameter="zen_action_plan.interval_type_reminder_1_quo", default='days')
    interval_number_reminder_2_quo = fields.Integer('2st Reminder', config_parameter="zen_action_plan.interval_number_reminder_2_quo")
    interval_type_reminder_2_quo = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Interval Type 2', config_parameter="zen_action_plan.interval_type_reminder_2_quo", default='days')
    interval_number_reminder_3_quo = fields.Integer('3rd Reminder', config_parameter="zen_action_plan.interval_number_reminder_3_quo")
    interval_type_reminder_3_quo = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Interval Type 3', config_parameter="zen_action_plan.interval_type_reminder_3_quo", default='days')
    interval_number_escalation_1_quo = fields.Integer('1st Escalation', config_parameter="zen_action_plan.interval_number_escalation_1_quo")
    interval_type_escalation_1_quo = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Escalation Type 1', config_parameter="zen_action_plan.interval_type_escalation_1_quo", default='days')
    interval_number_escalation_2_quo = fields.Integer('2st Reminder', config_parameter="zen_action_plan.interval_number_escalation_2_quo")
    interval_type_escalation_2_quo = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Interval Type 2', config_parameter="zen_action_plan.interval_type_escalation_2_quo", default='days')
    escalation_users_ids_quo_1 = fields.Many2many('hr.employee', 'res_config_users_crm_1',string='Escalation User 1st', compute="_compute_field_users_quo_1", inverse="_inverse_field_escalation_user_list_quo_1")
    escalation_users_list_quo_1 = fields.Char('escalation_users_list_1', config_parameter="zen_action_plan.escalation_users_list_quo_1")
    escalation_users_ids_quo_2 = fields.Many2many('hr.employee', 'res_config_users_crm_2',string='Escalation User 2nd', compute="_compute_field_users_quo_2", inverse="_inverse_field_escalation_user_list_quo_2")
    escalation_users_list_quo_2 = fields.Char('escalation_users_list_2', config_parameter="zen_action_plan.escalation_users_list_quo_2")

    #QUOTATION FUNCTION
    @api.depends('escalation_users_list_quo_1')
    def _compute_field_users_quo_1(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.escalation_users_list_quo_1:
                names = setting.escalation_users_list_quo_1.split(',')
                setting.escalation_users_ids_quo_1 = self.env['hr.employee'].search([('id', 'in', names)])
            else:
                setting.escalation_users_ids_quo_1 = None
    
    def _inverse_field_escalation_user_list_quo_1(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.escalation_users_ids_quo_1:
                setting.escalation_users_list_quo_1 = ','.join(str(e.id) for e in self.escalation_users_ids_quo_1)
            else:
                setting.escalation_users_list_quo_1 = ''


    @api.depends('escalation_users_list_quo_2')
    def _compute_field_users_quo_2(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.escalation_users_list_quo_2:
                names = setting.escalation_users_list_quo_2.split(',')
                setting.escalation_users_ids_quo_2 = self.env['hr.employee'].search([('id', 'in', names)])
            else:
                setting.escalation_users_ids_quo_2 = None
    
    def _inverse_field_escalation_user_list_quo_2(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.escalation_users_ids_quo_2:
                setting.escalation_users_list_quo_2 = ','.join(str(e.id) for e in self.escalation_users_ids_quo_2)
            else:
                setting.escalation_users_list_quo_2 = ''