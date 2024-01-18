import pytz
from odoo import models, fields, api,_
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    date_reminder_1 = fields.Date('1st Reminder')
    date_reminder_2 = fields.Date('2nd Reminder')
    date_escalation_1 = fields.Date('1st Escalation')
    date_escalation_2 = fields.Date('2nd Escalation')
    action_reminder_1 = fields.Boolean('Action Reminder 1st')
    action_reminder_2 = fields.Boolean('Action Reminder 2nd')
    action_escalation_1 = fields.Boolean('Action Escalation 1st')
    action_escalation_2 = fields.Boolean('Action Escalation 2nd')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CrmLead, self).create(vals_list)
        if res.stage_id.name == 'New' and res.type == 'opportunity':
            active_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.activate_reminder_crm')
            if active_reminder:
                    reminder_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_1_crm')
                    if reminder_1 != 0:
                        type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_1_crm')
                        if type_reminder == 'weeks':
                            date_reminder_1 = res.create_date + timedelta(weeks=int(reminder_1))
                            res.update({'date_reminder_1': date_reminder_1})
                        elif type_reminder == 'days':
                            date_reminder_1 = res.create_date + timedelta(days=int(reminder_1))
                            res.update({'date_reminder_1': date_reminder_1})

                    escalations_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_escalation_1_crm')
                    if escalations_1 != 0:
                        type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_escalation_1_crm')
                        if type_reminder == 'weeks':
                            date_escalation_1 = res.create_date + timedelta(weeks=int(escalations_1))
                            res.update({'date_escalation_1': date_escalation_1})
                        elif type_reminder == 'days':
                            date_escalation_1 = res.create_date + timedelta(days=int(escalations_1))
                            res.update({'date_escalation_1': date_escalation_1})
                    
                    reminder_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_2_crm')
                    if reminder_2 != 0:
                        type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_2_crm')
                        if type_reminder == 'weeks':
                            date_reminder_2 = res.create_date + timedelta(minutes=int(reminder_2))
                            res.update({'date_reminder_2': date_reminder_2})
                        elif type_reminder == 'days':
                            date_reminder_2 = res.create_date + timedelta(days=int(reminder_2))
                            res.update({'date_reminder_2': date_reminder_2})

                    escalations_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_escalation_2_crm')
                    if escalations_2 != 0:
                        type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_escalation_2_crm')
                        if type_reminder == 'week':
                            date_escalation_2 = res.create_date + timedelta(minutes=int(escalations_2))
                            res.update({'date_escalation_2': date_escalation_2})
                        elif type_reminder == 'days':
                            date_escalation_2 = res.create_date + timedelta(days=int(escalations_2))
                            res.update({'date_escalation_2': date_escalation_2})
        return res

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if 'type' in vals and vals['type'] == 'opportunity':
            for rec in self:
                if rec.stage_id.name == 'New' and rec.type == 'opportunity':
                    active_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.activate_reminder_crm')
                    if active_reminder:
                            reminder_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_1_crm')
                            if reminder_1 != 0:
                                type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_1_crm')
                                if type_reminder == 'weeks':
                                    date_reminder_1 = rec.write_date + timedelta(weeks=int(reminder_1))
                                    rec.update({'date_reminder_1': date_reminder_1})
                                elif type_reminder == 'days':
                                    date_reminder_1 = rec.write_date + timedelta(days=int(reminder_1))
                                    rec.update({'date_reminder_1': date_reminder_1})

                            escalations_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_escalation_1_crm')
                            if escalations_1 != 0:
                                type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_escalation_1_crm')
                                if type_reminder == 'weeks':
                                    date_escalation_1 = rec.write_date + timedelta(weeks=int(escalations_1))
                                    rec.update({'date_escalation_1': date_escalation_1})
                                elif type_reminder == 'days':
                                    date_escalation_1 = rec.write_date + timedelta(days=int(escalations_1))
                                    rec.update({'date_escalation_1': date_escalation_1})
                            
                            reminder_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_2_crm')
                            if reminder_2 != 0:
                                type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_2_crm')
                                if type_reminder == 'weeks':
                                    date_reminder_2 = rec.write_date + timedelta(minutes=int(reminder_2))
                                    rec.update({'date_reminder_2': date_reminder_2})
                                elif type_reminder == 'days':
                                    date_reminder_2 = rec.write_date + timedelta(days=int(reminder_2))
                                    rec.update({'date_reminder_2': date_reminder_2})

                            escalations_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_escalation_2_crm')
                            if escalations_2 != 0:
                                type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_escalation_2_crm')
                                if type_reminder == 'week':
                                    date_escalation_2 = rec.write_date + timedelta(minutes=int(escalations_2))
                                    rec.update({'date_escalation_2': date_escalation_2})
                                elif type_reminder == 'days':
                                    date_escalation_2 = rec.write_date + timedelta(days=int(escalations_2))
                                    rec.update({'date_escalation_2': date_escalation_2})
        return res

    @api.model
    def send_email_for_customer_and_sales_person(self):
        today = fields.date.today()
        _logger.info("==== ALREADY SCHEDULED REMINDER ======")
        _logger.info("Date: %s", today)
        self.reminder_one(today)
        self.reminder_two(today)
        self.escalation_one(today)
        self.escalation_two(today)
        return True

    #Reminder 1st Reminder To Customer And Sales Person
    def reminder_one(self, today):
        reminder_1 = self.search([('date_reminder_1', '<=', today), ('stage_id.name', '=', 'New'),('type', '=', 'opportunity'),('action_reminder_1', '=', False)])
        for r1 in reminder_1: 
            if r1.date_reminder_1:
                if r1.date_reminder_1 <= today: 
                    if r1.email_from:
                        #TEAM ESCALATION 1
                        escalation_list_1 = []
                        user_escalation_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_crm_1')
                        if user_escalation_1:
                            user_ids = user_escalation_1.split(',')
                            team_escalation_1 = self.env['hr.employee'].search([('id', 'in', user_ids)])
                            for es1 in team_escalation_1:
                                escalation_list_1.append({
                                    'name': es1.name,
                                    'email': es1.work_email,
                                    'phone': es1.mobile_phone
                                })
                        #END TEAM ESCALATION 1
                        #TEAM ESCALATION 2
                        escalation_list_2 = []
                        user_escalation_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_crm_2')
                        if user_escalation_2:
                            user_ids = user_escalation_2.split(',')
                            team_escalation_2 = self.env['hr.employee'].search([('id', 'in', user_ids)])
                            for es2 in team_escalation_2:
                                escalation_list_2.append({
                                    'name': es2.name,
                                    'email': es2.work_email,
                                    'phone': es2.mobile_phone
                                })
                        #END TEAM ESCALATION 2

                        #Email To Customer
                        email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                        sales_person = self.env['hr.employee'].search([('user_id','=',r1.user_id.id)],limit=1)
                        if sales_person:
                            sales_person_name = sales_person.name or ''
                            sales_person_email = sales_person.work_email or ''
                            sales_person_phone = sales_person.mobile_phone or ''
                            sales_person_signature = sales_person.user_id.signature or ''
                        if not sales_person:
                            user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                            sales_person_name = user_sakket.name or ''
                            sales_person_email = user_sakket.work_email or ''
                            sales_person_phone = user_sakket.mobile_phone or ''
                            sales_person_signature = sales_person.user_id.signature or ''

                        template_customer = self.env.ref('zen_action_plan.email_template_crm_to_customer_reminder_1', raise_if_not_found=False)
                        template_context = {
                            'sales_person_name': sales_person_name,
                            'sales_person_email': sales_person_email,
                            'sales_person_phone': sales_person_phone,
                            'sales_person_signature': sales_person_signature,
                            'user_escalation_one': escalation_list_1,
                            'user_escalation_two': escalation_list_2
                        }
                        template_customer.with_context(**template_context).send_mail(r1.id, force_send=True, email_values={'email_to': r1.email_from, 'email_from': email_company,'reply_to':email_company}, email_layout_xmlid='mail.mail_notification_light')
                        #End Email To Customer

                        # Send email Sales Person
                        template_sales_person = self.env.ref('zen_action_plan.email_template_crm_to_sales_person_reminder_1', raise_if_not_found=False)
                        template_context_sale_person = {
                            'sales_person_name': sales_person_name
                        }
                        template_sales_person.with_context(**template_context_sale_person).send_mail(r1.id, force_send=True, email_values={'email_to': sales_person_email, 'email_from': email_company, 'reply_to':email_company }, email_layout_xmlid='mail.mail_notification_light')
                    r1.write({'action_reminder_1': True})
        return True
    
    #Reminder 2nd Reminder To Sales Person
    def reminder_two(self, today):
        reminder_2 = self.search([('date_reminder_2', '<=', today), ('stage_id.name', '=', 'New'), ('type', '=', 'opportunity'), ('action_reminder_2', '=', False)])
        for r2 in reminder_2: 
            # Send email to Customer
            if r2.date_reminder_1:
                if r2.date_reminder_1 <= today: 
                    if r2.email_from:
                        # Send email Sales Person
                        email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                        sales_person = self.env['hr.employee'].search([('user_id','=',r2.user_id.id)],limit=1)
                        if sales_person:
                            sales_person_name = sales_person.name or ''
                            sales_person_email = sales_person.work_email or ''
                        if not sales_person:
                            user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                            sales_person_name = user_sakket.name or ''
                            sales_person_email = user_sakket.work_email or ''

                        
                        template_sales_person = self.env.ref('zen_action_plan.email_template_crm_to_sales_person_reminder_2', raise_if_not_found=False)
                        email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                        template_context_sale_person = {
                            'sales_person_name': sales_person_name,
                        }
                        template_sales_person.with_context(**template_context_sale_person).send_mail(r2.id, force_send=True, email_values={'email_to': sales_person_email, 'email_from': email_company, 'reply_to': email_company}, email_layout_xmlid='mail.mail_notification_light')
                    r2.write({'action_reminder_2': True})
        return True
    
    #Reminder 1nd Reminder To Escalation 1st
    def escalation_one(self, today):
        escalation_1 = self.search([('date_escalation_1', '<=', today), ('stage_id.name', '=', 'New'),('type', '=', 'opportunity'),('action_escalation_1', '=', False)])
        for es1 in escalation_1:
            if es1.date_escalation_1:
                if es1.date_escalation_1 <= today:
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    escalation_list_1 = []
                    user_escalation_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_crm_1')
                    if user_escalation_1:
                        user_ids = user_escalation_1.split(',')
                        team_escalation_1 = self.env['hr.employee'].search([('id', 'in', user_ids)])
                        for us1 in team_escalation_1:
                            escalation_list_1.append(us1.work_email)
                    elif not user_escalation_1:
                        user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                        escalation_list_1.append(user_sakket.work_email)
                    
                    #Sales Person Details
                    sales_person = self.env['hr.employee'].search([('user_id','=',es1.user_id.id)],limit=1)
                    if sales_person:
                        sales_person_name = sales_person.name or ''
                        sales_person_email = sales_person.work_email or ''
                        sales_person_phone = sales_person.mobile_phone or ''
                    if not sales_person:
                        user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                        sales_person_name = user_sakket.name or ''
                        sales_person_email = user_sakket.work_email or ''
                        sales_person_phone = user_sakket.mobile_phone or ''
                    
                    if len(team_escalation_1) > 1:
                        email_escalation_1 = ', '.join(escalation_list_1)
                    elif len(team_escalation_1) == 1:
                        email_escalation_1 = str(escalation_list_1[0])
                    #Send Email
                    template_escalation_1 = self.env.ref('zen_action_plan.email_template_crm_to_escalation_user_1', raise_if_not_found=False)
                    template_context = {
                        'sales_person_name': sales_person_name,
                        'sales_person_email': sales_person_email,
                        'sales_person_phone': sales_person_phone,
                    }
                    template_context['email_to'] = escalation_list_1
                    template_escalation_1.with_context(**template_context).send_mail(es1.id, force_send=True, email_values={'email_to':email_escalation_1, 'email_from': email_company,'reply_to':email_company}, email_layout_xmlid='mail.mail_notification_light')
                es1.write({'action_escalation_1': True})

    # Reminder To Escalation 2nd
    def escalation_two(self, today):
        escalation_2 = self.search([('date_escalation_2', '<=', today), ('stage_id.name', '=', 'New'),('type', '=', 'opportunity'),('action_escalation_2', '=', False)])
        for es2 in escalation_2:
            if es2.date_escalation_2:
                if es2.date_escalation_2 <= today:
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    escalation_list_2 = []
                    user_escalation_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_crm_2')
                    if user_escalation_2:
                        user_ids = user_escalation_2.split(',')
                        team_escalation_2 = self.env['hr.employee'].search([('id', 'in', user_ids)])
                        for us2 in team_escalation_2:
                            escalation_list_2.append(us2.work_email)
                    elif not user_escalation_2:
                        user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                        escalation_list_2 .append(user_sakket.work_email)
                    
                    #CC Escalation 1st
                    escalation_list_1 = []
                    user_escalation_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_crm_1')
                    if user_escalation_1:
                        user_ids = user_escalation_1.split(',')
                        team_escalation_1 = self.env['hr.employee'].search([('id', 'in', user_ids)])
                        for us1 in team_escalation_1:
                            escalation_list_1.append(us1.work_email)
                    elif not user_escalation_1:
                        user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                        escalation_list_1.append(user_sakket.work_email)

                                        
                    #Sales Person Details
                    sales_person = self.env['hr.employee'].search([('user_id','=',es2.user_id.id)],limit=1)
                    if sales_person:
                        sales_person_name = sales_person.name or ''
                        sales_person_email = sales_person.work_email or ''
                        sales_person_phone = sales_person.mobile_phone or ''
                    if not sales_person:
                        user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                        sales_person_name = user_sakket.name or ''
                        sales_person_email = user_sakket.work_email or ''
                        sales_person_phone = user_sakket.mobile_phone or ''
                    
                    if len(team_escalation_1) > 1:
                        email_escalation_1 = ', '.join(escalation_list_1)
                    if len(team_escalation_1) == 1:
                        email_escalation_1 = str(escalation_list_1[0])
                    if len(team_escalation_2) > 1:
                        email_escalation_2= ', '.join(escalation_list_2)
                    if len(team_escalation_2) == 1:
                        email_escalation_2 = str(escalation_list_2[0])
                    
                    #Send Email
                    template_escalation_2 = self.env.ref('zen_action_plan.email_template_crm_to_escalation_user_2', raise_if_not_found=False)
                    template_context = {
                        'sales_person_name': sales_person_name,
                        'sales_person_email': sales_person_email,
                        'sales_person_phone': sales_person_phone,
                    }
                    template_context['email_to'] = escalation_list_2
                    template_context['email_cc'] = escalation_list_1
                    template_escalation_2.with_context(**template_context).send_mail(es2.id, force_send=True, email_values={'email_to':email_escalation_2,'email_cc': email_escalation_1, 'email_from': email_company,'reply_to':email_company}, email_layout_xmlid='mail.mail_notification_light')
                es2.write({'action_escalation_2': True})