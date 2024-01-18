import base64
from odoo import models, fields, api
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_reminder_1 = fields.Date('1st Reminder')
    date_reminder_2 = fields.Date('2nd Reminder')
    date_reminder_3 = fields.Date('3rd Reminder')
    date_escalation_1 = fields.Date('1st Escalation')
    date_escalation_2 = fields.Date('2st Escalation')
    action_reminder_1 = fields.Boolean('Action Reminder 1st')
    action_reminder_2 = fields.Boolean('Action Reminder 2nd')
    action_reminder_3 = fields.Boolean('Action Reminder 3rd')
    action_escalation_1 = fields.Boolean('Action Escalation 1st')
    action_escalation_2 = fields.Boolean('Action Escalation 2nd')


    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        if res.state == 'draft' or res.state == 'sent':
            active_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.activate_reminder_quotation')
            if active_reminder:
                reminder_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_1_quo')
                if reminder_1 != 0:
                    type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_1_quo')
                    if type_reminder == 'weeks':
                        date_reminder_1 = res.create_date + timedelta(weeks=int(reminder_1))
                        res.update({'date_reminder_1': date_reminder_1})
                    elif type_reminder == 'days':
                        date_reminder_1 = res.create_date + timedelta(days=int(reminder_1))
                        res.update({'date_reminder_1': date_reminder_1})
                    
                reminder_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_2_quo')
                if reminder_2 != 0:
                    type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_2_quo')
                    if type_reminder == 'weeks':
                        date_reminder_2 = res.create_date + timedelta(weeks=int(reminder_2))
                        res.update({'date_reminder_2': date_reminder_2})
                    elif type_reminder == 'days':
                        date_reminder_2 = res.create_date + timedelta(days=int(reminder_2))
                        res.update({'date_reminder_2': date_reminder_2})
                    
                reminder_3 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_reminder_3_quo')
                if reminder_3 != 0:
                    type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_reminder_3_quo')
                    if type_reminder == 'weeks':
                        date_reminder_3 = res.create_date + timedelta(weeks=int(reminder_3))
                        res.update({'date_reminder_3': date_reminder_3})
                    elif type_reminder == 'days':
                        date_reminder_3 = res.create_date + timedelta(days=int(reminder_3))
                        res.update({'date_reminder_3': date_reminder_3})
                    
                escalations_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_escalation_1_quo')
                if escalations_1 != 0:
                    type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_escalation_1_quo')
                    if type_reminder == 'weeks':
                        date_escalation_1 = res.create_date + timedelta(weeks=int(escalations_1))
                        res.update({'date_escalation_1': date_escalation_1})
                    elif type_reminder == 'days':
                        date_escalation_1 = res.create_date + timedelta(days=int(escalations_1))
                        res.update({'date_escalation_1': date_escalation_1})
                    
                escalations_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_number_escalation_2_quo')
                if escalations_2 != 0:
                    type_reminder = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.interval_type_escalation_2_quo')
                    if type_reminder == 'weeks':
                        date_escalation_2 = res.create_date + timedelta(weeks=int(escalations_2))
                        res.update({'date_escalation_2': date_escalation_2})
                    elif type_reminder == 'days':
                        date_escalation_2 = res.create_date + timedelta(days=int(escalations_2))
                        res.update({'date_escalation_2': date_escalation_2})
        
        return res
    
    
    
    @api.model
    def send_email_for_customer_and_sales_person(self):
        today = fields.date.today()
        self.reminder_one(today)
        self.reminder_two(today)
        self.reminder_three(today)
        self.escalation_one(today)
        self.escalation_two(today)
        return True

    def reminder_one(self, today):
        reminder_1 = self.search([('date_reminder_1', '<=', today), ('state', '=', 'sent'), ('action_reminder_1', '=', False)])
        for r1 in reminder_1:
            if r1.date_reminder_1:
                if r1.date_reminder_1 <= today: 
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    # Send email to Customer
                    if r1.partner_id.email:
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
                        email_context = {**self.env.context.copy(), **{
                                        'sales_person_name': sales_person_name,
                                        'sales_person_email': sales_person_email,
                                        'sales_person_phone': sales_person_phone,
                                        'sales_person_signature': sales_person_signature,
                                    }
                                }
                        template_customer = self.env.ref('zen_action_plan.email_template_sales_order_to_customer_reminder_1')
                        r1.with_context(email_context).message_post_with_template(
                            template_customer.id,
                            composition_mode='comment',
                            email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
                            
                        )
                    r1.write({'action_reminder_1': True})
    
    def reminder_two(self, today):
        reminder_2 = self.search([('date_reminder_2', '<=', today), ('state', '=', 'sent'), ('action_reminder_2', '=', False)])
        for r2 in reminder_2:
            if r2.date_reminder_2:
                if r2.date_reminder_2 <= today: 
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    # Send email to Customer
                    if r2.partner_id.email:
                        email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                        sales_person = self.env['hr.employee'].search([('user_id','=',r2.user_id.id)],limit=1)
                        if sales_person:
                            sales_person_name = sales_person.name or ''
                            sales_person_email = sales_person.work_email or ''
                        if not sales_person:
                            user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                            sales_person_name = user_sakket.name or ''
                            sales_person_email = user_sakket.work_email or ''

                        
                        template_sales_person = self.env.ref('zen_action_plan.email_template_sales_order_to_sales_person_reminder_2', raise_if_not_found=False)
                        template_context_sale_person = {
                            'sales_person_name': sales_person_name,
                        }
                        template_sales_person.with_context(**template_context_sale_person).send_mail(r2.id, force_send=True, email_values={'email_to': sales_person_email, 'email_from': email_company, 'reply_to': email_company}, email_layout_xmlid='mail.mail_notification_light')
                    r2.write({'action_reminder_2': True})
    
    def reminder_three(self, today):
        reminder_3 = self.search([('date_reminder_3', '<=', today), ('state', '=', 'sent'), ('action_reminder_3', '=', False)])
        for r3 in reminder_3:
            if r3.date_reminder_3:
                if r3.date_reminder_3 <= today: 
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    # Send email to Customer
                    if r3.partner_id.email:
                        email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                        sales_person = self.env['hr.employee'].search([('user_id','=',r3.user_id.id)],limit=1)
                        if sales_person:
                            sales_person_name = sales_person.name or ''
                            sales_person_email = sales_person.work_email or ''
                        if not sales_person:
                            user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
                            sales_person_name = user_sakket.name or ''
                            sales_person_email = user_sakket.work_email or ''

                        template_sales_person = self.env.ref('zen_action_plan.email_template_sales_order_to_sales_person_reminder_3', raise_if_not_found=False)
                        template_context_sale_person = {
                            'sales_person_name': sales_person_name,
                        }
                        template_sales_person.with_context(**template_context_sale_person).send_mail(r3.id, force_send=True, email_values={'email_to': sales_person_email, 'email_from': email_company, 'reply_to': email_company}, email_layout_xmlid='mail.mail_notification_light')
                    r3.write({'action_reminder_3': True})
        
    def escalation_one(self, today):
        escalation_1 = self.search([('date_escalation_1', '<=', today), ('state', '=', 'sent'),('action_escalation_1', '=', False)])
        for es1 in escalation_1:
            if es1.date_escalation_1:
                if es1.date_escalation_1 <= today:
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    escalation_list_1 = []
                    user_escalation_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_quo_1')
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
                    template_escalation_1 = self.env.ref('zen_action_plan.email_template_sales_order_to_escalation_user_1', raise_if_not_found=False)
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
        escalation_2 = self.search([('date_escalation_2', '<=', today), ('state', '=', 'sent'),('action_escalation_2', '=', False)])
        for es2 in escalation_2:
            if es2.date_escalation_2:
                if es2.date_escalation_2 <= today:
                    email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                    escalation_list_2 = []
                    user_escalation_2 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_quo_1')
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
                    user_escalation_1 = self.env['ir.config_parameter'].sudo().get_param('zen_action_plan.escalation_users_list_quo_2')
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
                    template_escalation_2 = self.env.ref('zen_action_plan.email_template_sales_order_to_escalation_user_2', raise_if_not_found=False)
                    template_context = {
                        'sales_person_name': sales_person_name,
                        'sales_person_email': sales_person_email,
                        'sales_person_phone': sales_person_phone,
                    }
                    template_context['email_to'] = escalation_list_2
                    template_context['email_cc'] = escalation_list_1
                    template_escalation_2.with_context(**template_context).send_mail(es2.id, force_send=True, email_values={'email_to':email_escalation_2,'email_cc': email_escalation_1, 'email_from': email_company,'reply_to':email_company}, email_layout_xmlid='mail.mail_notification_light')
                es2.write({'action_escalation_2': True})