from odoo import http, SUPERUSER_ID, _
from odoo.http import request
import markupsafe
# from odoo.addons.mail.controllers.discuss import DiscussController
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context


# class MailMessage(DiscussController):
class ThreadController(http.Controller):
    def mail_message_post(self,thread_model, thread_id, post_data, **kwargs):
        if 'body' in post_data:
            if post_data['message_type'] == 'comment':
                if thread_model == 'crm.lead':   
                    active_chatter_in_crm = request.env['ir.config_parameter'].sudo().get_param('zen_mail_message.active_chatter_in_crm')
                    if active_chatter_in_crm:
                        body_email_old = post_data['body']
                        partner_ids = []
                        lead_ids = request.env[thread_model].browse(int(thread_id))
                        for follower in lead_ids.message_follower_ids:
                            if lead_ids.partner_id.id != follower.partner_id.id:
                                partner_ids.append({
                                    'name': follower.partner_id.name,
                                    'email': follower.partner_id.email
                                })
                            modified_body_email = body_email_old
                            if partner_ids:
                                table = '<br/><br/><br/><span style="font-style: italic">Reply to this email will be delivered to : </span><ul>'
                                for partner_info in partner_ids:
                                    table += f'<li>{partner_info["name"]} &lt;{partner_info["email"]}&gt;</li>'
                                table += '</ul>'
                                post_data['body'] = markupsafe.Markup(str(modified_body_email) + '\n' + table)
                if thread_model == 'sale.order':   
                    active_chatter_in_crm = request.env['ir.config_parameter'].sudo().get_param('zen_mail_message.active_chatter_in_sale')
                    if active_chatter_in_crm:
                        body_email_old = post_data['body']
                        partner_ids = []
                        sale_ids = request.env[thread_model].browse(int(thread_id))
                        for follower in sale_ids.message_follower_ids:
                            if sale_ids.partner_id.id != follower.partner_id.id:
                                partner_ids.append({
                                    'name': follower.partner_id.name,
                                    'email': follower.partner_id.email
                                })
                            modified_body_email = body_email_old
                            if partner_ids:
                                table = '<br/><br/><br/><span style="font-style: italic">Reply to this email will be delivered to : </span><ul>'
                                for partner_info in partner_ids:
                                    table += f'<li>{partner_info["name"]} &lt;{partner_info["email"]}&gt;</li>'
                                table += '</ul>'
                                post_data['body'] = markupsafe.Markup(str(modified_body_email) + '\n' + table)
                if thread_model == 'purchase.order':   
                    active_chatter_in_crm = request.env['ir.config_parameter'].sudo().get_param('zen_mail_message.active_chatter_in_purchase')
                    if active_chatter_in_crm:
                        body_email_old = post_data['body']
                        partner_ids = []
                        purchase_ids = request.env[thread_model].browse(int(thread_id))
                        for follower in purchase_ids.message_follower_ids:
                            if purchase_ids.partner_id.id != follower.partner_id.id:
                                partner_ids.append({
                                    'name': follower.partner_id.name,
                                    'email': follower.partner_id.email
                                })
                            modified_body_email = body_email_old
                            if partner_ids:
                                table = '<br/><br/><br/><span style="font-style: italic">Reply to this email will be delivered to : </span><ul>'
                                for partner_info in partner_ids:
                                    table += f'<li>{partner_info["name"]} &lt;{partner_info["email"]}&gt;</li>'
                                table += '</ul>'
                                post_data['body'] = markupsafe.Markup(str(modified_body_email) + '\n' + table)
        values = super().mail_message_post(thread_model, thread_id, post_data, **kwargs)
        return values