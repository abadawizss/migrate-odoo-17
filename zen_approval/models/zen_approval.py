
from datetime import datetime
import json
import re
from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class SalesOrderApproval(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('draft',),('waiting_approved', 'Waiting Approval'),('approved', 'Approved'),('sent',),('reject', 'Reject')], default="draft")
    exception_ids = fields.One2many('zen.sale.order.exception', 'order_id', string='Exceptions')
    layer = fields.Selection([
        ('one', 'one'),
        ('two', 'two'),
    ], string='Step', default="two")
    user_approved_discount = fields.Boolean('User Approved Discount', compute='_show_button_approve_exception_discount')
    user_approved_payment = fields.Boolean('User Appoved Payment',compute='_show_button_approve_exception_payment')
    document_state = fields.Selection([
        ('none', 'None'),
        ('is_locked', 'Is Locked'),
        ('is_revision', 'Is Revision'),
    ], string='document_state', default='none')
    #! Additional field
    is_approved = fields.Boolean('Is Approved', compute='_compute_is_approved')

    def vals_payment_term(self, payment, payment_names):
        vals_payment_term = {
            'exception_name': 'Payment Term',
            'normal': str(payment_names),
            'approved_payment': True,
            'status': 'pending',
            'order_id': self.id,
            'current': payment.name,
            'payment_term_id': payment.id
        }
        return vals_payment_term
    
    def vals_discount(self, line, discount_model):
        exception = 'Discount on ' + line.product_id.name
        current = line.discount
        formula_normal_current = current - discount_model
        amount_discount = (line.price_unit * line.product_uom_qty * (formula_normal_current / 100))
        vals = {
            'product_id': line.product_id.id,
            'exception_name': exception,
            'normal': str(discount_model) + '%',
            'status': 'pending',
            'approved_discount': True,
            'order_id': line.order_id.id,
            'current': str(current) + '%',
            'order_line_id': line.id,
            'amount': amount_discount
        }
        return vals
    
    def vals_freight_charge(self):
        amount_untaxed = amount_tax = 0.0
        for line in self.order_line:
            amount_untaxed += line.price_subtotal
            amount_tax += line.price_tax
        if amount_untaxed != 0:
            if amount_untaxed >= 200000:
                freight_charges = 0.0
            elif amount_untaxed <= 200000:
                freight_charges = max(amount_untaxed * 0.0113, 400)
                freight_charges = round(freight_charges, 0)
            else:
                freight_charges = 0.0
        
        vals_freight = {
            'exception_name': 'Freight Charges',
            'normal': 'Include',
            'current': 'Exclude',
            'approved_payment': True,
            'status': 'pending',
            'order_id': self.id,
            'amount': freight_charges
        }
        return vals_freight
    

    
    @api.onchange('order_line.discount','order_line.price_unit','order_line.product_uom_qty', 'is_approved')
    def _compute_is_approved(self):
        for record in self:
            request_approval = []
            exception_list = []
            user_approval_discount = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_discount')
            user_approval_payment_term= self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_payment_term')
            active_approval_freight= self.env['ir.config_parameter'].sudo().get_param('zen_freight_management.activate_freight_charges')
            #APPROVAL DISCOUNT AND FREIGHT
            if user_approval_discount and not user_approval_payment_term:
                for line in record.order_line:
                    contact_type = line.order_id.partner_id.contact_type
                    product_qty = line.product_uom_qty
                    discount_model = line.get_applicable_discount(line.product_id, contact_type, product_qty)
                    percentage_discount_end_user = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.percentage_discount')
                    #ADD CONDITIONAL END USERS
                    if not discount_model and line.order_id.partner_id.contact_type == 'end_user' and line.discount > float(percentage_discount_end_user):
                        discount_model = float(percentage_discount_end_user)
                    vals_discount = self.vals_discount(line,discount_model)
                    #END ADD CONDITIONAL END USERS
                    if line.display_type not in ('line_section','line_note'):
                        if record.state == 'draft':
                            #NOT YET REVISION
                            if record.document_state == 'none':
                                #DISCOUNT 
                                exception_ids = record.env['zen.sale.order.exception'].search([('order_line_id','=', line.id)])
                                if not exception_ids:
                                    if discount_model and line.discount > discount_model:
                                        exception_list.append((0,0, vals_discount))
                                        approval = True
                                        request_approval.append(approval)
                                elif exception_ids:
                                    for exception_id in exception_ids:
                                        if discount_model and line.discount > discount_model:
                                            exception_id.write(vals_discount)
                                            approval = True
                                            request_approval.append(approval)
                                        else:
                                            exception_id.sudo().unlink()
                                            approval = False
                                            request_approval.append(approval)
                                
                            #IS REVISION
                            elif record.document_state == 'is_revision':
                                #Status Discount Approved or Reject
                                exception_all_state_ids = record.env['zen.sale.order.exception'].search([('order_line_id','=', line.id),('status','!=', 'pending')])
                                if exception_all_state_ids:
                                    status_discount = []
                                    for discount_value in exception_all_state_ids:
                                        original_discount_value = float(discount_value.current.strip('%'))
                                        status_discount.append(original_discount_value)
                                    exception_pending = record.env['zen.sale.order.exception'].search([('status','=', 'pending'),('order_line_id','=', line.id)])
                                    status_ex = []
                                    for excep_all in exception_all_state_ids:
                                        status_ex.append(excep_all.status)
                                    if not exception_pending:
                                        if discount_model and line.discount > discount_model and 'reject' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = True
                                                request_approval.append(approval)
                                        elif discount_model and line.discount > discount_model and 'approve' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = False
                                                request_approval.append(approval)
                                    elif exception_pending:
                                        exception_pending.sudo().unlink()
                                        if discount_model and line.discount > discount_model and 'reject' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = True
                                                request_approval.append(approval)
                                        elif discount_model and line.discount > discount_model and 'approve' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = False
                                                request_approval.append(approval)
                                        else:
                                            approval = False
                                            request_approval.append(approval)
                                         

                #FREIGHT CHARGES
                if active_approval_freight:
                    exception_ids_freight = record.env['zen.sale.order.exception'].search([('exception_name','=','Freight Charges'),('order_id','=', record.id)])
                    if not exception_ids_freight:
                        if record.exclude:
                            vals_freight = self.vals_freight_charge()
                            exception_list.append((0,0,vals_freight))
                            approval = True
                            request_approval.append(approval)
                    elif exception_ids_freight:
                        if not record.exclude:
                            approval = False
                            request_approval.append(approval)
            
            #APPROVAL PAYMENT TERM AND FREIGHT
            elif not user_approval_discount and user_approval_payment_term:
                payment_term_list = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.payment_term_list')
                payment_ids = [int(term_id) for term_id in payment_term_list.split(',')]
                payment_terms = self.env['account.payment.term'].sudo().search([('id', 'in', payment_ids)])
                payment_names = ' or '.join(term.name for term in payment_terms)
                payment_in_config = record.payment_term_id.id not in payment_ids                                  
                vals_payment_term = self.vals_payment_term(record.payment_term_id,payment_names)
                
                #PAYMENT TERM
                if record.state == 'draft':
                    if record.document_state == 'none':
                        exception_ids_payment = record.env['zen.sale.order.exception'].search([('exception_name','=','Payment Term'),('order_id','=', record.id)])
                        if not exception_ids_payment:
                            if payment_in_config:
                                exception_list.append((0,0,vals_payment_term))
                                approval = True
                                request_approval.append(approval)
                        elif exception_ids_payment:
                            if payment_in_config:
                                if exception_ids_payment != record.payment_term_id:
                                    exception_ids_payment.write(vals_payment_term)
                                    approval = True
                                    request_approval.append(approval)
                            else:
                                exception_ids_payment.sudo().unlink()
                    
                    if record.document_state == 'is_revision':
                        exception_all_ids_payment = record.env['zen.sale.order.exception'].search([('exception_name','=','Payment Term'),('order_id','=', record.id),('status','!=', 'pending')])
                        if exception_all_ids_payment:
                            status_payment =[]
                            for payment_value in exception_all_ids_payment:
                                status_payment.append(payment_value.payment_term_id.id)
                            exception_payment_pending = record.env['zen.sale.order.exception'].search([('exception_name','=','Payment Term'),('order_id','=', record.id),('status','=', 'pending')])
                            status_payment_ex =[]
                            for excep_pay_all in exception_all_ids_payment:
                                status_payment_ex.append(excep_pay_all.status)
                            if not exception_payment_pending:
                                if payment_in_config and 'reject' in status_payment_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = True
                                        request_approval.append(approval)
                                elif payment_in_config and 'approve' in status_payment_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = False
                                        request_approval.append(approval)
                            elif exception_payment_pending:
                                exception_payment_pending.sudo().unlink()
                                if payment_in_config and 'reject' in status_payment_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = True
                                        request_approval.append(approval)
                                elif payment_in_config and 'approve' in status_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = False
                                        request_approval.append(approval)
                                else:
                                    approval = False
                                    request_approval.append(approval)
                    
                    
                
                #FREIGHT CHARGES
                if active_approval_freight:
                    exception_ids_freight = record.env['zen.sale.order.exception'].search([('exception_name','=','Freight Charges'),('order_id','=', record.id)])
                    if not exception_ids_freight:
                        if record.exclude:
                            vals_freight = self.vals_freight_charge()
                            exception_list.append((0,0,vals_freight))
                            approval = True
                            request_approval.append(approval)
                    elif exception_ids_freight:
                        if not record.exclude:
                            approval = False
                            request_approval.append(approval)

            #APPROVAL PAYMENT, FREIGHT, DISCOUNT
            elif user_approval_discount and user_approval_payment_term:
                for line in record.order_line:
                    contact_type = line.order_id.partner_id.contact_type
                    product_qty = line.product_uom_qty
                    discount_model = line.get_applicable_discount(line.product_id, contact_type, product_qty)
                    percentage_discount_end_user = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.percentage_discount')
                    #ADD CONDITIONAL END USERS
                    if not discount_model and line.order_id.partner_id.contact_type == 'end_user' and line.discount > float(percentage_discount_end_user):
                        discount_model = float(percentage_discount_end_user)
                    vals_discount = self.vals_discount(line,discount_model)
                    #END ADD CONDITIONAL END USERS
                    if line.display_type not in ('line_section','line_note'):
                        if record.state == 'draft':
                            #BELUM DI REVISI
                            if record.document_state == 'none':
                                #DISCOUNT 
                                exception_ids = record.env['zen.sale.order.exception'].search([('order_line_id','=', line.id)])
                                if not exception_ids:
                                    if discount_model and line.discount > discount_model:
                                        exception_list.append((0,0, vals_discount))
                                        approval = True
                                        request_approval.append(approval)
                                elif exception_ids:
                                    for exception_id in exception_ids:
                                        if discount_model and line.discount > discount_model:
                                            exception_id.write(vals_discount)
                                            approval = True
                                            request_approval.append(approval)
                                        else:
                                            exception_id.sudo().unlink()
                                            approval = False
                                            request_approval.append(approval)

                            #IS REVISION
                            elif record.document_state == 'is_revision':
                                #Status Discount Approved or Reject
                                exception_all_state_ids = record.env['zen.sale.order.exception'].search([('order_line_id','=', line.id),('status','!=', 'pending')])
                                if exception_all_state_ids:
                                    status_discount = []
                                    for discount_value in exception_all_state_ids:
                                        original_discount_value = float(discount_value.current.strip('%'))
                                        status_discount.append(original_discount_value)
                                    exception_pending = record.env['zen.sale.order.exception'].search([('status','=', 'pending'),('order_line_id','=', line.id)])
                                    status_ex = []
                                    for excep_all in exception_all_state_ids:
                                        status_ex.append(excep_all.status)
                                    if not exception_pending:
                                        if discount_model and line.discount > discount_model and 'reject' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = True
                                                request_approval.append(approval)
                                        elif discount_model and line.discount > discount_model and 'approve' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = False
                                                request_approval.append(approval)
                                    elif exception_pending:
                                        exception_pending.sudo().unlink()
                                        if discount_model and line.discount > discount_model and 'reject' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = True
                                                request_approval.append(approval)
                                        elif discount_model and line.discount > discount_model and 'approve' in status_ex:
                                            if line.discount not in status_discount:
                                                approval = True
                                                request_approval.append(approval)
                                                exception_list.append((0,0, vals_discount))
                                            else:
                                                approval = False
                                                request_approval.append(approval)
                                        else:
                                            approval = False
                                            request_approval.append(approval)
                                         
                payment_term_list = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.payment_term_list')
                payment_ids = [int(term_id) for term_id in payment_term_list.split(',')]
                payment_terms = self.env['account.payment.term'].sudo().search([('id', 'in', payment_ids)])
                payment_names = ' or '.join(term.name for term in payment_terms)
                payment_in_config = record.payment_term_id.id not in payment_ids                                  
                vals_payment_term = self.vals_payment_term(record.payment_term_id,payment_names)
                
                #PAYMENT TERM
                if record.state == 'draft':
                    if record.document_state == 'none':
                        exception_ids_payment = record.env['zen.sale.order.exception'].search([('exception_name','=','Payment Term'),('order_id','=', record.id)])
                        if not exception_ids_payment:
                            if payment_in_config:
                                exception_list.append((0,0,vals_payment_term))
                                approval = True
                                request_approval.append(approval)
                        elif exception_ids_payment:
                            if payment_in_config:
                                if exception_ids_payment != record.payment_term_id:
                                    exception_ids_payment.write(vals_payment_term)
                                    approval = True
                                    request_approval.append(approval)
                            else:
                                exception_ids_payment.sudo().unlink()
                    
                    if record.document_state == 'is_revision':
                        exception_all_ids_payment = record.env['zen.sale.order.exception'].search([('exception_name','=','Payment Term'),('order_id','=', record.id),('status','!=', 'pending')])
                        if exception_all_ids_payment:
                            status_payment =[]
                            for payment_value in exception_all_ids_payment:
                                status_payment.append(payment_value.payment_term_id.id)
                            exception_payment_pending = record.env['zen.sale.order.exception'].search([('exception_name','=','Payment Term'),('order_id','=', record.id),('status','=', 'pending')])
                            status_payment_ex =[]
                            for excep_pay_all in exception_all_ids_payment:
                                status_payment_ex.append(excep_pay_all.status)
                            if not exception_payment_pending:
                                if payment_in_config and 'reject' in status_payment_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = True
                                        request_approval.append(approval)
                                elif payment_in_config and 'approve' in status_payment_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = False
                                        request_approval.append(approval)
                            elif exception_payment_pending:
                                exception_payment_pending.sudo().unlink()
                                if payment_in_config and 'reject' in status_payment_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = True
                                        request_approval.append(approval)
                                elif payment_in_config and 'approve' in status_ex:
                                    if record.payment_term_id.id not in status_payment:
                                        approval = True
                                        request_approval.append(approval)
                                        exception_list.append((0,0, vals_payment_term))
                                    else:
                                        approval = False
                                        request_approval.append(approval)
                                else:
                                    approval = False
                                    request_approval.append(approval)
                
                
                
                #FREIGHT CHARGES
                if active_approval_freight:
                    exception_ids_freight = record.env['zen.sale.order.exception'].search([('exception_name','=','Freight Charges'),('order_id','=', record.id)])
                    if not exception_ids_freight:
                        if record.exclude:
                            vals_freight = self.vals_freight_charge()
                            exception_list.append((0,0,vals_freight))
                            approval = True
                            request_approval.append(approval)
                    elif exception_ids_freight:
                        if not record.exclude:
                            approval = False
                            request_approval.append(approval)
            
            #ONLY FREIGHT CHARGES
            elif not user_approval_discount and not user_approval_payment_term:
                #FREIGHT CHARGES
                if active_approval_freight:
                    exception_ids_freight = record.env['zen.sale.order.exception'].search([('exception_name','=','Freight Charges'),('order_id','=', record.id)])
                    if not exception_ids_freight:
                        if record.exclude:
                            vals_freight = self.vals_freight_charge()
                            exception_list.append((0,0,vals_freight))
                            approval = True
                            request_approval.append(approval)
                    elif exception_ids_freight:
                        if not record.exclude:
                            approval = False
                            request_approval.append(approval)
                

            record.exception_ids = exception_list                         
            result_app = request_approval
            result = True in result_app
            record.is_approved = result    
            if record.is_approved:
                record.layer = 'one'
            else:
                record.layer = 'two'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state in ('draft','approved')).with_context(tracking_disable=True).write({'state': 'sent'})
        return super(SalesOrderApproval, self.with_context(mail_post_autofollow=self.env.context.get('mail_post_autofollow', True))).message_post(**kwargs)
    
    def action_quotation_sent(self):
        """ Mark the given draft quotation(s) as sent.

        :raise: UserError if any given SO is not in draft state.
        """
        if self.filtered(lambda so: so.state not in ('draft','approved')):
            raise UserError(_("Only draft and Approved orders can be marked as sent directly."))

        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)

        self.write({'state': 'sent'})
        
    def _show_button_approve_exception_discount(self):
        for record in self:
            list_user_discount = []
            user_approval= self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_discount')
            if user_approval:
                user_approval_discount = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.user_approval_list')
                if user_approval_discount:
                    user_ids = user_approval_discount.split(',')
                    approval_ids = self.env['hr.employee'].sudo().search([('id', 'in', user_ids)])
                    list_user_discount = approval_ids.mapped('user_id.id')

                    record.user_approved_discount = self.env.user.id in list_user_discount
                else:
                    record.user_approved_discount = False
            else:
                record.user_approved_discount = False

    def _show_button_approve_exception_payment(self):
        for record in self:
            list_user_payment = []
            user_approval= self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_payment_term')
            user_approval_payment = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.user_approval_list_payment_term')
            if user_approval:
                if user_approval_payment:
                    user_ids = user_approval_payment.split(',')
                    approval_ids = self.env['hr.employee'].sudo().search([('id', 'in', user_ids)])
                    list_user_payment = approval_ids.mapped('user_id.id')

                    record.user_approved_payment = self.env.user.id in list_user_payment
                else:
                    record.user_approved_payment = False
            else:
                record.user_approved_payment = False

    
   
    def action_request_approved(self):
        list_status = []
        for rec in self.exception_ids:
            list_status.append(rec.status)
        if 'pending' not in list_status:
            raise ValidationError(_("The account is already in use in a 'sale' or 'purchase' journal. This means that the account's type couldn't be 'receivable' or 'payable'."))

        form_view_id = self.env.ref('zen_approval.sale_order_mention_reason_view').id
        action =  {
            'name': _('Mention Reason Extra Discount, Payment Term & Freight Charges'),
            'view_mode': 'form',
            'res_model': 'sale.order.mention.reason',
            'view_id': form_view_id,
            'views': [(form_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return action

    

    def action_withdraw_request(self):
        return self.write({'state':'draft', 'document_state': 'is_revision'})
    
    def action_approved(self):
        raise UserError(_('Check the Exceptions tab to further Approve'))

    def action_reject(self):
        raise UserError(_('Check the Exceptions tab to further Reject'))
    
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # status_ex = fields.Selection([
    #     ('approval_required', 'Approval Required'),
    #     ('no_approval_required', 'No approval required'),
    # ], string='Status Exception', compute='_get_state_exception')
    
    # def _get_state_exception(self):
    #     for rec in self:
    #         rec.status_ex  = False
    #         exception_state = self.env['zen.sale.order.exception'].search([('order_line_id','=', rec.id)],limit=1)
    #         if exception_state:
    #             rec.status_ex = exception_state.status
    
    @api.onchange('product_id', 'product_uom_qty')
    def onchange_product_id(self):
        if self.product_id and self.order_id.partner_id:
            discount_model = 0
            contact_type = self.order_id.partner_id.contact_type
            #! === VALIDATE CONTACT TYPE === #
            if not contact_type:
                raise UserError(_('Please check contact type customer')) 
            #! === VALIDATE CONTACT TYPE === #
            contact_type = self.order_id.partner_id.contact_type
            product_qty = self.product_uom_qty
            discount_model = self.get_applicable_discount(self.product_id, contact_type, product_qty)
            self.discount = discount_model
            
    def get_applicable_discount(self, product, contact_type, quantity):
        discounts = False
        user_approval= self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_discount')
        if user_approval:
            if contact_type == 'end_user':
                percentage_discount_end_user = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.percentage_discount')
                if percentage_discount_end_user:
                    discounts = 0
            elif contact_type == 'dealer':
                discount_group = self.env['zen.discount.group'].sudo().search([('discount_group_ids','=',product.id)])
                if discount_group:
                    discounts = self.env['zen.discount'].sudo().search([
                    ('group_id', '=', discount_group.id),
                    ('minimum_qty', '<=', quantity),
                    ('maximum_qty', '>=', quantity),
                ], order='maximum_discount_percentage DESC', limit=1).maximum_discount_percentage

        return discounts if discounts else False
    
class SalesOrderException(models.Model):
    _name = 'zen.sale.order.exception'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_id = fields.Many2one('sale.order', string='Order ID', ondelete='cascade')
    order_line_id = fields.Many2one('sale.order.line', string='order_line', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='product', tracking=True)
    exception_name = fields.Char('Exception')
    normal = fields.Char('Normal')
    current = fields.Char('Current') 
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approve', 'Approved'),
        ('reject', 'Reject')
    ], string='Status', tracking=3)  
    approved_discount = fields.Boolean('Approval Discount')
    approved_payment = fields.Boolean('Approval Payment')
    user_approved_discount = fields.Boolean('User Approved Discount', compute='_show_button_approve_exception_discount')
    user_approved_payment = fields.Boolean('User Appoved Payment',compute='_show_button_approve_exception_payment')
    amount = fields.Float('Amount')
    payment_term_id = fields.Many2one('account.payment.term', string='payment_term')
    request_date = fields.Datetime('Request Date')
    approver_action_date = fields.Datetime('Approver Action Date')
    
    def _show_button_approve_exception_discount(self):
        for record in self:
            if record.order_id.state == 'waiting_approved':
                if record.approved_discount:
                    list_user_discount = []
                    user_approval= self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_discount')
                    if user_approval:
                        user_approval_discount = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.user_approval_list')
                        if user_approval_discount:
                            user_ids = user_approval_discount.split(',')
                            approval_ids = self.env['hr.employee'].sudo().search([('id', 'in', user_ids)])
                            list_user_discount = approval_ids.mapped('user_id.id')

                            record.user_approved_discount = self.env.user.id in list_user_discount
                        else:
                            record.user_approved_discount = False
                    else:
                        record.user_approved_discount = False
                else:
                    record.user_approved_discount = False
            else:
                record.user_approved_discount = False

    def _show_button_approve_exception_payment(self):
        for record in self:
            if record.order_id.state == 'waiting_approved':
                if record.approved_payment:
                    list_user_payment = []
                    user_approval= self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.activate_approval_payment_term')
                    user_approval_payment = self.env['ir.config_parameter'].sudo().get_param('zen_sale_order.user_approval_list_payment_term')
                    if user_approval:
                        if user_approval_payment:
                            user_ids = user_approval_payment.split(',')
                            approval_ids = self.env['hr.employee'].sudo().search([('id', 'in', user_ids)])
                            list_user_payment = approval_ids.mapped('user_id.id')

                            record.user_approved_payment = self.env.user.id in list_user_payment
                        else:
                            record.user_approved_payment = False
                    else:
                        record.user_approved_payment = False
                else:
                    record.user_approved_payment = False
            else:
                record.user_approved_payment = False

    def action_exception_approve(self):
        date = fields.Datetime.now()
        self.write({'status': 'approve', 'approver_action_date': date})
        

    def action_exception_reject(self):
        form_view_id = self.env.ref('zen_approval.sale_order_reject_exception_view').id
        action =  {
            'name': _('Reason Reject Exception'),
            'view_mode': 'form',
            'res_model': 'reject.exception',
            'view_id': form_view_id,
            'views': [(form_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return action

    def write(self, vals):
        list_status = []
        res = super(SalesOrderException, self).write(vals)
        for rec in self.order_id.exception_ids:
            list_status.append(rec.status)
        if list_status:
            if 'pending' not in list_status:
                if 'reject' in list_status:
                    self.order_id.write({'state': 'draft','document_state': 'is_revision'})
                else:
                    self.order_id.write({'state': 'approved', 'document_state': 'is_locked', 'layer': 'two'})
            elif 'pending' in list_status:
                pass

        return res
    