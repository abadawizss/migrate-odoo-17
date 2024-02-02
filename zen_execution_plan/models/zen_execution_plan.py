from datetime import datetime
import json
import re
from odoo import api, models, fields,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    execution_ids = fields.One2many('zen.sale.execution', 'order_id', string='execution')

    @api.constrains('order_line', 'order_line.product_uom_qty')
    def check_execution_quantity(self):
        if self.execution_ids:
            for order in self:
                for line in order.order_line:
                    total_execution_qty = sum(order.execution_ids.filtered(lambda r: r.product_id == line.product_id).mapped('qty'))
                    if total_execution_qty != line.product_uom_qty:
                        raise ValidationError(f"The number of executions for the product {line.product_id.name} in the Sales Order {order.name} does not match the total Sales Order Line.")

                    date_schedule_list = order.execution_ids.filtered(lambda r: r.product_id == line.product_id).mapped('date_schedule')
                    for date_schedule in date_schedule_list:
                        if date_schedule and date_schedule < order.date_order:
                            raise ValidationError(f"The execution date for the product {line.product_id.name} in the Sales Order {order.name} is smaller than the order date.")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.execution_ids:
            for exc in self.execution_ids:
                exc.write({'status': 'scheduled'})
        return res


class SalesOrderExecution(models.Model):
    _name = 'zen.sale.execution'

    order_id = fields.Many2one('sale.order', string='Order ID')
    product_id = fields.Many2one('product.product', string='Product Name')
    qty = fields.Float('Qty', default=1)
    date_schedule = fields.Datetime('Date Schedule')
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled')
    ], string='Status')      

    @api.onchange('order_id', 'product_id')
    def onchange_order_id_product_id(self):
        if self.order_id:
            product_list = []
            for rec in self.order_id.order_line:
                if rec.product_id.product_tmpl_id.detailed_type == 'product':
                    product_list.append(rec.product_id.id)
            res = {'domain': {'product_id': [('id', 'in', product_list)]}}
            return res

    @api.model
    def send_reminder_execution_plan(self):
        today = datetime.now()
        execution_plan = self.search([('order_id.state','=','sale'),('date_schedule','<=',today)])
        if execution_plan:
            for record in execution_plan:
                if record.status == 'scheduled':
                    if record.date_schedule <= today:
                        update = record.write({'status': 'delayed'})
                    if update == True: 
                        email_company = self.env['hr.employee'].search([('name','ilike','Administrator')],limit=1).work_email
                        sales_team = []
                        member_team = self.env['crm.team'].search([('id','=',record.order_id.team_id.id)])
                        for user in member_team.member_ids:
                            sales_team.append(user.login)
                        if sales_team:
                            if len(sales_team) > 1:
                                email_to = ', '.join(sales_team)
                            elif len(member_team) == 1:
                                email_to = str(sales_team[0])
                        #Send Email
                        template = self.env.ref('zen_execution_plan.email_template_execution_plan', raise_if_not_found=False)
                        template.send_mail(record.id, force_send=True, email_values={'email_to':email_to, 'email_from': email_company,'reply_to':email_company}, email_layout_xmlid='mail.mail_notification_light')