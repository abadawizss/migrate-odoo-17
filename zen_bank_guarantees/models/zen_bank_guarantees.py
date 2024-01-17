# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class ZenBankGuarantees(models.Model):
    _name = 'zen.bank.guarantees'
    _description = 'Zen Bank Guarantees'
    _rec_name = 'bg_number'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    sales_order_id = fields.Many2one('sale.order', string='Sales Order', required=False)
    issuing_bank = fields.Char(string='Issuer Bank')
    type = fields.Selection([
                ('dd_deposit', 'DD deposit'),
                ('fix_deposit', 'FD deposit'),
                ('check_deposit', 'Check Deposit'),
                ('bank_guarantee', 'Bank Guarantee')
            ], string='Type', default='bank_guarantee')
    date_of_issuance = fields.Date(string='Date of Issuance')
    release_due_date = fields.Date(string='Release Due Date')

    sale_order_count = fields.Integer(compute='_compute_sale_order_count')
    sale_order_ids = fields.Many2many('sale.order', 'sale_order_zen_bank_guarantees_rel', 'zen_bank_guarantees_id',
                                      'sale_order_id', string='Related Sale Orders', copy=False)

    #additional field 20231218
    bg_number = fields.Char('Bank Guarantees Number', default='/')
    po_number = fields.Char('PO Number')
    expiry_date = fields.Date('Expiry Date')
    state = fields.Selection([
                ('submission', 'Submission Pending'),
                ('submitted', 'Submitted'),
                ('expired', 'Expired'),
                ('recovered', 'Recovered'),
                ('replaced', 'Replaced')
            ], string='State', default='submission', tracking=3)
    document_count = fields.Integer(compute='_compute_document_count')
    # validity_amount = fields.Float('Validation Amount')
    # validity_date_from = fields.Date('Valid From')
    # validity_date_to = fields.Date('Valid To')
    bg_amount = fields.Float('Bank Guarantee Amount')
    bank_guarantees_ids = fields.One2many('zen.bank.guarantees.line', 'bank_guarantees_id', string='History')
    active_notification = fields.Boolean('Activated Email Notification', default=True)
    description = fields.Text(string="Remarks")
    po_date = fields.Date('PO Date')
    bg_reference_number = fields.Char('BG Reference Number')
    show_replace_number = fields.Boolean('Show Replace Number', compute='_show_replace_number')
    replace_number = fields.Integer('Replace Number')
    # po_reference = fields.Char('PO Reference')
    #End additional 20231218

    _sql_constraints = [
        ('name_bank_guarantee_unique', 'UNIQUE(bg_number)', 'You cannot have the same Bank Guarantees twice, Please Refresh Browser and Try Again')
    ]

    @api.constrains('date_of_issuance','release_due_date','expiry_date')
    def _check_validation_date(self):
        for rec in self:
            if rec.expiry_date < rec.date_of_issuance and rec.release_due_date < rec.date_of_issuance:
                raise ValidationError('BG Expiry Date and BG Release Due Date can not be before BG Issue Date!')
            if rec.expiry_date < rec.date_of_issuance:
                raise ValidationError('BG Expiry Date can not be before BG Issue Date!')
            if rec.release_due_date < rec.date_of_issuance:
                raise ValidationError('BG Release Due Date can not be before BG Issue Date!')

    def action_reset_to_draft(self):
        self.write({'state': 'submission'})

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done_or_cancel(self):
        for ml in self:
            if ml.state != 'submission':
                raise UserError(_("Sorry, You can't delete Bank Guarantees that has already been Expired or Submitted"))

    def _show_replace_number(self):
        for record in self:
            if record.replace_number == 0:
                record.show_replace_number = False
            elif record.replace_number > 0:
                record.show_replace_number = True

    def get_revision_number(self, bank):
        if not bank.replace_number:
            return 1
        else:
            rev = bank.replace_number + 1
            return rev

    #additional 20231218
    @api.onchange('customer_id','sales_order_id')
    def onchange_customer(self):
        res = {}
        if self.customer_id and not self.sales_order_id:
            sale_order_ids = self.env['sale.order'].search([('partner_id', '=', self.customer_id.id)])
            list_so = [(so.id) for so in sale_order_ids]
            res = {'domain': {'sales_order_id': [('id', 'in', list_so)]}}
        elif self.sales_order_id and not self.customer_id:
            sale_order = self.env['sale.order'].browse(self.sales_order_id.id)
            res = {
                'domain': {'customer_id': [('id', '=', sale_order.partner_id.id)]},
                'value': {'customer_id': sale_order.partner_id.id}
            }
        elif not self.customer_id and not self.sales_order_id:
            res = {'domain': {'customer_id': [], 'sales_order_id': []},
                'value': {'customer_id': False, 'sales_order_id': False}}
        return res
    
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['documents.document'].search_count([('bank_guarantees_id','=', rec.id)])

    @api.model
    def create(self, vals):
        if vals.get('bg_number', '/') == '/':
            vals['bg_number'] = self.env['ir.sequence'].next_by_code('zen.bank.guarantees') or '/'
        res = super(ZenBankGuarantees, self).create(vals)
        return res

    def action_view_document(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'documents.document',
            'view_mode': 'tree',
            'view_id': False,
            'context': "{'create': False}",
            'views': [(self.env.ref('documents.documents_view_list').id, 'tree')],
            'domain': [('bank_guarantees_id','=',self.id)],
            'target': 'current',
        }
        return action

    def action_submitted(self):
        self.sudo().write({'state': 'submitted'})

    def action_recovered(self):
        self.write({'state': 'recovered'})

    def action_replaced(self):
        self.write({'state': 'replaced'})

    def action_renew(self):
        new_sequence_bg = self.get_revision_number(self)
        sequence = f"{self.bg_number} R.{new_sequence_bg}"
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Bank Guarantees Renew / Replace',
            'res_model': 'zen.bank.guarantees.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': 
                {
                    'default_replace_number': new_sequence_bg,
                    'default_bank_guarantees_id': self.id,
                    'default_bank_guarantee_number': sequence,
                    'default_customer_id': self.customer_id.id,
                    'default_sales_order_id': self.sales_order_id.id,
                    'default_po_number': self.po_number,
                    'default_po_date': self.po_date,
                    'default_state': self.state
                },
        }
        return action

    @api.model
    def reminder_expired_document(self):
        for doc in self.search([('state', '=', 'submitted'), ('active_notification', '=', True)]):
            kolkata_tz = pytz.timezone('Asia/Kolkata')
            current_date = datetime.now(kolkata_tz).date()
            expiry_date = doc.expiry_date
            notification_intervals = [30, 20, 10, 5, 1]
            for interval in notification_intervals:
                notification_date = expiry_date - timedelta(days=interval)
                _logger.info("current_date: %s", current_date) 
                _logger.info("notification_date: %s", notification_date) 
                _logger.info("state: %s", doc.state) 
                if current_date == notification_date:
                    _logger.info("==== 1 ======")
                    self.send_email_reminder(doc, interval)
                elif current_date >= expiry_date:
                    _logger.info("==== 2 ======")
                    doc.sudo().write({'state': 'expired'})

    def send_email_reminder(self, document, interval):
        customer_name = document.sales_order_id.partner_id.name
        email_company = self.env.companies.email
        sale_person_ids = self.env['hr.employee'].search([('user_id','=',document.sales_order_id.user_id.id)],limit=1)
        if sale_person_ids:
            sales_person_name = sale_person_ids.name or ''
            sales_person_email = sale_person_ids.work_email or ''
            sales_person_phone = sale_person_ids.mobile_phone or ''
        else:
            user_sakket = self.env['hr.employee'].search([('user_id.name','ilike','saket')],limit=1)
            sales_person_name = user_sakket.name or ''
            sales_person_email = user_sakket.work_email or ''
            sales_person_phone = user_sakket.mobile_phone or ''

        template_customer = self.env.ref('zen_bank_guarantees.email_template_expired_bank_guarantees', raise_if_not_found=False)
        template_context = {
            'interval': interval,
            'customer_name': customer_name,
            'sales_person_name': sales_person_name,
            'sales_person_email': sales_person_email,
            'sales_person_phone': sales_person_phone,
        }
        res = template_customer.with_context(**template_context).send_mail(document.id, force_send=True, email_values={'email_to': document.customer_id.email, 'email_cc': sales_person_email, 'email_from': email_company,'reply_to':email_company}, email_layout_xmlid='mail.mail_notification_light')
        return res

    #End additional 20231218
    @api.depends('sales_order_id')
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sales_order_id.zen_bank_guarantees_ids.ids)

    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['context'] = {
            'search_default_zen_bank_guarantees_ids': [self.sales_order_id.zen_bank_guarantees_ids.ids],
            'default_zen_bank_guarantees_ids': [(4, self.sales_order_id.zen_bank_guarantees_ids.ids)],
        }
        action['domain'] = [('zen_bank_guarantees_ids', 'in', self.sales_order_id.zen_bank_guarantees_ids.ids)]
        return action


class ZenBankGuaranteesLine(models.Model):
    _name = 'zen.bank.guarantees.line'
    _description = 'Zen Bank Guarantees'

    bank_guarantees_id = fields.Many2one('zen.bank.guarantees', string='BG ID')
    bank_guarantee_number = fields.Char('BG Number Previous')
    # renew_date = fields.Date(string="Renew Date", default=fields.Date.today)
    issue_date = fields.Date('BG Issue Date')
    release_date = fields.Date('BG Release Due Date')
    bank_expiry_date = fields.Date(string="BG Expiry Date", readonly=True)
    description = fields.Text(string="Remarks")
    state = fields.Selection([
                ('submission', 'Submission Pending'),
                ('submitted', 'Submitted'),
                ('expired', 'Expired'),
                ('recovered', 'Recovered'),
                ('replaced', 'Replaced')
            ], string='State')
    bg_amount = fields.Float('Bank Guarantee Amount')


class DocumentsFolder(models.Model):
    _inherit = 'documents.document'

    bank_guarantees_id = fields.Many2one('zen.bank.guarantees', string='Bank Guarantees')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    zen_bank_guarantees_ids = fields.One2many('zen.bank.guarantees', 'sales_order_id', string='Bank Guarantees')
    zen_bank_guarantees_line = fields.One2many('zen.bank.guarantees', 'sales_order_id', string='Bank Guarantees')

    def action_view_zen_bank_guarantees(self):
        self.ensure_one()
        action = self.env.ref('zen_bank_guarantees.action_view_zen_bank_guarantees').read()[0]
        action['context'] = {
            'search_default_sale_order_id': self.id,
        }
        return action

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.zen_bank_guarantees_line.write({'customer_id': self.partner_id.id})

    # def write(self, vals):
    #     res = super(SaleOrder, self).write(vals)
    #     if 'partner_id' in self:
    #         for order in self:
    #             order.zen_bank_guarantees_line.write({'customer_id': order.partner_id.id})
    #     return res
    #
    # @api.model
    # def create(self, vals):
    #     order = super(SaleOrder, self).create(vals)
    #     if 'partner_id' in vals:
    #         order.zen_bank_guarantees_line.write({'customer_id': order.partner_id.id})
    #     return order

    # def action_create_bank_guarantee(self):
    #     for order in self:
    #         vals = {
    #             'issuing_bank': order.issuing_bank,
    #             'sales_order_id': order.id,
    #             'customer_id': order.sale_order_id.partner_id.id,
    #         }
    #         order.zen_bank_guarantees_ids = [(0, 0, vals)]


class IrAttachments(models.Model):
    _inherit = 'ir.attachment'

    def _post_add_create(self):
        if self.res_model == 'zen.bank.guarantees':
            bank_guarantees_ids = self.env[self.res_model].search([('id','=', self.res_id)])
            for bank in bank_guarantees_ids:
                if bank.sales_order_id.id:
                    #! Folder Finance
                    finance_folder = self.env['documents.folder'].search([('name','=','Finance')])
                    if finance_folder:
                        folder_root = finance_folder
                    if not finance_folder:
                        folder_vals = {
                            'name': 'Finance',
                        }
                        folder_root = self.env['documents.folder'].create(folder_vals)
                    #* Folder BGs
                    bg_folder = self.env['documents.folder'].search([('name','=','BGs')])
                    if bg_folder:
                        folder_bg = bg_folder
                    if not bg_folder:
                        folder_bg_vals = {
                            'name': 'BGs',
                            'parent_folder_id': folder_root.id,
                        }
                        folder_bg = self.env['documents.folder'].create(folder_bg_vals)

                    sequence_folder = f"{bank.sales_order_id.name}"
                    folder_so = self.env['documents.folder'].search([('parent_folder_id', '=', folder_bg.id),('name', '=', sequence_folder)], limit=1)
                    if not folder_so:
                        folder_so_vals = {
                                'name': sequence_folder,
                                'parent_folder_id': folder_bg.id,
                            }
                        folder_sale_order = self.env['documents.folder'].create(folder_so_vals)
                    if folder_so:
                        folder_sale_order = folder_so

                    attachment_name = f"{bank.bg_number}"
                    existing_folder_bank = self.env['documents.folder'].search([('parent_folder_id', '=', folder_sale_order.id),('name', '=', attachment_name)], limit=1)
                    if existing_folder_bank:
                        folder_bank = existing_folder_bank
                    if not existing_folder_bank:
                        folder_vals = {
                            'name': attachment_name,
                            'parent_folder_id': folder_sale_order.id,
                        }
                        folder_bank = self.env['documents.folder'].create(folder_vals)
                    document_vals = {
                            'name': self.name,
                            'datas': self.datas,
                            'folder_id': folder_bank.id,
                            'type': 'binary',
                            'sale_order_id': bank.sales_order_id.id,
                            'lead_id': bank.sales_order_id.opportunity_id.id if bank.sales_order_id.opportunity_id.id else False ,
                            'bank_guarantees_id': bank.id
                        }
                    self.env['documents.document'].sudo().create(document_vals)
        res = super(IrAttachments, self)._post_add_create()
        return res        
    # def _post_add_create(self):
    #     res = super(IrAttachments, self)._post_add_create()
    #     if self.res_model == 'zen.bank.guarantees':
    #         bank_guarantees_ids = self.env[self.res_model].search([('id','=', self.res_id)])
    #         for bank in bank_guarantees_ids:
    #             if bank.sales_order_id.id:
    #                 sequence_folder = f"{bank.sales_order_id.name}"
    #                 parent_folder_so = self.env['documents.folder'].search([('name', '=', sequence_folder)], limit=1)
    #                 if parent_folder_so:
    #                     attachment_name = f"{bank.bg_number}"
    #                     existing_folder = self.env['documents.folder'].search([('name', '=', attachment_name)], limit=1)
    #                     if existing_folder:
    #                         print("Folder Bank Guarantes")
    #                         folder_bank = existing_folder

    #                     else:
    #                         folder_vals = {
    #                             'name': attachment_name,
    #                             'parent_folder_id': parent_folder_so.id,
    #                         }
    #                         folder_bank = self.env['documents.folder'].create(folder_vals)
    #                     document_vals = {
    #                         'name': self.name,
    #                         'datas': self.datas,
    #                         'folder_id': folder_bank.id,
    #                         'type': 'binary',
    #                         'sale_order_id': bank.sales_order_id.id,
    #                         'lead_id': bank.sales_order_id.opportunity_id.id if bank.sales_order_id.opportunity_id.id else False ,
    #                         'bank_guarantees_id': bank.id
    #                     }
    #                     self.env['documents.document'].sudo().create(document_vals)
    #                 return res