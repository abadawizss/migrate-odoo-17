# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from datetime import timedelta, datetime
import pytz
import urllib
import json
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    product_name = fields.Char('Product Name')
    inquiry_type = fields.Selection([('W', 'Direct Inquiry'), ('B', 'Purchased BL'), ('P', 'Call Enquiry')], 'Inquiry Type')
    enq_call_duration = fields.Char('Enquiry Call Duration')
    alt_email = fields.Char('Alternate Email')
    alt_mobile = fields.Char('Alternate Mobile')
    alt_phone = fields.Char('Alternate Phone')
    sender_name = fields.Char("Sender Name")
    query_id = fields.Char(string="UNIQUE_QUERY_ID")
    query_time = fields.Datetime('Query Time')

    @api.model
    def update_indiamart(self):
        configuration = self.env['indiamart.configuration'].search([('state','=', 'confirm')])
        for conf in configuration:
            user_tz = self.env.user.tz
            _logger.info("user: %s", self.env.user)
            _logger.info("user_tz: %s", user_tz)
            if not user_tz:
                _logger.info("User timezone is not defined so assuming it to be GMT.")
                user_tz = 'GMT'
            if conf.start_date and conf.end_date:
                date_start = conf.start_date.astimezone(pytz.timezone(user_tz)).strftime('%d-%m-%Y%H:%M:%S')
                date_end = conf.end_date.astimezone(pytz.timezone(user_tz)).strftime('%d-%m-%Y%H:%M:%S')
            elif conf.start_date and not conf.end_date:
                date_start = conf.start_date.astimezone(pytz.timezone(user_tz)).strftime('%d-%m-%Y%H:%M:%S')
                date_end = datetime.now(pytz.timezone(user_tz)).strftime('%d-%m-%Y%H:%M:%S')
            else:
                indiamart_lead = self.env['crm.lead'].search([('source_id.name','=','IndiaMart'),('query_time','!=',False)], order='query_time desc', limit=1)
                indiamart_lead_start_timestamp = indiamart_lead.query_time + timedelta(seconds=1)
                date_end = datetime.now(pytz.timezone(user_tz)).strftime('%d-%m-%Y%H:%M:%S')
                date_start = indiamart_lead_start_timestamp.strftime('%d-%m-%Y%H:%M:%S')
            
            
            if conf.mobile_key and conf.state == 'confirm':
                url = "https://mapi.indiamart.com/wservce/crm/crmListing/v2/?glusr_crm_key="+str(conf.mobile_key)+"&start_time="+date_start+"&end_time="+date_end
                update_lead =self._update_lead(url)
            return True
    
    def _update_lead(self, url):
        contents = urllib.request.urlopen(url).read()
        if contents.decode('UTF-8') not in ('null', '[]'):
            data = json.loads(contents.decode('UTF-8'))
            _logger.info("==== ALREADY SCHEDULE INDIAMART ======")
            _logger.info("RESPONSE INDIAMART: %s", data)
            _logger.info("URL: %s", url)
            for data_list in data.get('RESPONSE'):
                if not self.search([('query_id','=', str(data_list.get('UNIQUE_QUERY_ID')))]):
                    sales_team = self.env['crm.team'].search([('name','ilike', 'Sales')], limit=1).id
                    sales_person = self.env['hr.employee'].search([('user_id.name','ilike', 'Marketing Team')], limit=1)
                    source = self.env['utm.source'].search([('name','ilike', 'Indiamart')], limit=1)
                    state_ids = self.env['res.country.state'].sudo().search([('name','ilike',data_list.get('SENDER_STATE'))],limit=1)
                    if not source:
                        source = self.env['utm.source'].sudo().create({
                            'name': 'Indiamart',
                        })
                    
                    
                    if data_list.get('SENDER_COMPANY'):
                        company_ids = self.env['res.partner'].sudo().search([('name','=',  data_list.get('SENDER_COMPANY')), ('city','=', data_list.get('SENDER_CITY')), ('is_company','=', True)], limit=1).id
                        if  not company_ids:
                            company = {
                                'name': data_list.get('SENDER_COMPANY') or '' ,
                                'is_company': True,
                                # 'email': data_list.get('SENDER_EMAIL') or '',
                                # 'mobile': data_list.get('SENDER_MOBILE') or '',
                                # 'phone': data_list.get('SENDER_PHONE') or '',
                                'street': data_list.get('SENDER_ADDRESS') or '',
                                'city': data_list.get('SENDER_CITY') or '',
                                'state_id': state_ids.id,
                            }
                            new_company = self.env['res.partner'].sudo().create(company)
                            company_ids = new_company.id
                        else:
                            company_ids = company_ids
                    elif not data_list.get('SENDER_COMPANY'):
                        company_ids = False
                    partner_ids = self.env['res.partner'].sudo().search([('name','=', data_list.get('SENDER_NAME')), ('email','=', data_list.get('SENDER_EMAIL')), ('is_company','=', False)])
                    if not partner_ids:
                        partner = {
                            'name': data_list.get('SENDER_NAME') or '',
                            'parent_id': company_ids,
                            'email': data_list.get('SENDER_EMAIL') or '',
                            'is_company': False,
                            'mobile': data_list.get('SENDER_MOBILE') or '',
                            'phone': data_list.get('SENDER_PHONE') or '',
                            'street': data_list.get('SENDER_ADDRESS') or '',
                            'city': data_list.get('SENDER_CITY') or '',
                            'state_id': state_ids.id,
                        }
                        partner_ids = self.env['res.partner'].sudo().create(partner)
                    stage_ids = self.env['crm.stage'].search([('name','=','New')],limit=1)
                    leads = self.env['crm.lead'].create({
                        'name': data_list.get('SUBJECT') or '',
                        'query_time': data_list.get('QUERY_TIME') or '',
                        'sender_name': partner_ids.name,
                        'product_name': data_list.get('QUERY_PRODUCT_NAME') or '',
                        'partner_id': partner_ids.id if partner_ids else False,
                        'email_from': partner_ids.email,
                        'phone': partner_ids.phone,
                        'mobile': partner_ids.mobile,
                        # add city and state_id 20231229
                        'city': partner_ids.city,
                        'state_id': partner_ids.state_id.id,
                        # end add city and state_id 20231229
                        'inquiry_type': data_list.get('QUERY_TYPE'),
                        'enq_call_duration': data_list.get('CALL_DURATION') or '',
                        'street': partner_ids.street,
                        'alt_email': data_list.get('SENDER_EMAIL_ALT') or '',
                        'alt_mobile': data_list.get('SENDER_MOBILE_ALT') or '',
                        'alt_phone': data_list.get('SENDER_PHONE_ALT') or '',
                        'description': data_list.get('QUERY_MESSAGE') or '',
                        'query_id': data_list.get('UNIQUE_QUERY_ID'),
                        'user_id': sales_person.user_id.id,
                        'team_id': sales_team,
                        'source_id': source.id,
                        'stage_id': stage_ids.id
                    })
                    _logger.info("LEAD ID: %s", leads)
                    
                    
