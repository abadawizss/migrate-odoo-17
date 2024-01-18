from odoo import models, fields, api
from datetime import datetime, timedelta


class ConfigurationReminderCRM(models.TransientModel):
    _inherit = 'res.config.settings'

    #CRM REMINDER
    activate_reminder_crm = fields.Boolean(string='Reminder Email CRM', config_parameter="zen_action_plan.activate_reminder_crm")
    interval_number_reminder_1_crm = fields.Integer('1st Reminder to Salesperson + Information Customer', config_parameter="zen_action_plan.interval_number_reminder_1_crm")
    interval_type_reminder_1_crm = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Interval Type 1', config_parameter="zen_action_plan.interval_type_reminder_1_crm", default='days')
    interval_number_reminder_2_crm = fields.Integer('2nd Reminder to Salesperson', config_parameter="zen_action_plan.interval_number_reminder_2_crm")
    interval_type_reminder_2_crm = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='Interval Type 2', config_parameter="zen_action_plan.interval_type_reminder_2_crm", default='days')
    interval_number_escalation_1_crm = fields.Integer('1st Escalation Recipients + Information Customer', config_parameter="zen_action_plan.interval_number_escalation_1_crm")
    interval_type_escalation_1_crm = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='1st Escalation Recipients', config_parameter="zen_action_plan.interval_type_escalation_1_crm", default='days')
    escalation_users_ids_crm_1 = fields.Many2many('hr.employee', 'res_config_users_crm_1',string='1st Users Escalation Recipients', compute="_compute_field_users_1", inverse="_inverse_field_escalation_user_list_1")
    escalation_users_list_crm_1 = fields.Char('escalation_users_list_1', config_parameter="zen_action_plan.escalation_users_list_crm_1")
    interval_number_escalation_2_crm = fields.Integer('2nd Escalation Recipients', config_parameter="zen_action_plan.interval_number_escalation_2_crm")
    interval_type_escalation_2_crm = fields.Selection([
        ('week', 'weeks'),
        ('days', 'days')
    ], string='2nd Escalation Recipients', config_parameter="zen_action_plan.interval_type_escalation_2_crm", default='days')
    escalation_users_ids_crm_2 = fields.Many2many('hr.employee', 'res_config_users_crm_2',string='1st Users Escalation Recipients', compute="_compute_field_users_2", inverse="_inverse_field_escalation_user_list_2")
    escalation_users_list_crm_2 = fields.Char('escalation_users_list_2', config_parameter="zen_action_plan.escalation_users_list_crm_2")


    #USER ESCALATION 1ST
    @api.depends('escalation_users_list_crm_1')
    def _compute_field_users_1(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.escalation_users_list_crm_1:
                names = setting.escalation_users_list_crm_1.split(',')
                setting.escalation_users_ids_crm_1 = self.env['hr.employee'].search([('id', 'in', names)])
            else:
                setting.escalation_users_ids_crm_1 = None
    
    def _inverse_field_escalation_user_list_1(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.escalation_users_ids_crm_1:
                setting.escalation_users_list_crm_1 = ','.join(str(e.id) for e in self.escalation_users_ids_crm_1)
            else:
                setting.escalation_users_list_crm_1 = ''
    #END USER ESCALATION 1ST
    
    #USER ESCALATION 2ND
    @api.depends('escalation_users_list_crm_2')
    def _compute_field_users_2(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.escalation_users_list_crm_2:
                names = setting.escalation_users_list_crm_2.split(',')
                setting.escalation_users_ids_crm_2 = self.env['hr.employee'].search([('id', 'in', names)])
            else:
                setting.escalation_users_ids_crm_2 = None
    
    def _inverse_field_escalation_user_list_2(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.escalation_users_ids_crm_2:
                setting.escalation_users_list_crm_2 = ','.join(str(e.id) for e in self.escalation_users_ids_crm_2)
            else:
                setting.escalation_users_list_crm_2 = ''
    
    #USER ESCALATION 2ND