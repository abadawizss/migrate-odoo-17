from odoo import models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
class ZenBankGuaranteesRenewWizard(models.TransientModel):
    _name = 'zen.bank.guarantees.renew.wizard'
    _description = 'Bank Guarantees Renew'
    
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    sales_order_id = fields.Many2one('sale.order', string='Sales Order', required=False)
    bank_guarantees_id = fields.Many2one('zen.bank.guarantees', string='BG ID')
    bank_guarantee_number = fields.Char('Bank Guarantees Number')
    issue_date = fields.Date(string="BG Issue Date", required=True)
    release_date = fields.Date(string="BG Release Due Date")
    expiry_date = fields.Date(string="BG Expiry Date")
    description = fields.Text(string="Remarks")
    issuing_bank = fields.Char(string='Issuer Bank')
    bg_reference_number = fields.Char('BG Reference Number')
    po_number = fields.Char('PO Number')
    po_date = fields.Date('PO Date')
    state = fields.Selection([
        ('submission', 'Submission Pending'),
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
        ('recovered', 'Recovered'),
        ('replaced', 'Replaced')
    ], string='State')
    type = fields.Selection([
        ('cash_deposit', 'Cash deposit'),
        ('dd_deposit', 'DD deposit'),
        ('fix_deposit', 'FD deposit'),
        ('check_deposit', 'Check Deposit'),
        ('bank_guarantee', 'Bank Guarantee')
    ], string='Type', default='bank_guarantee')
    bg_amount = fields.Float('Bank Guarantee Amount')
    replace_number = fields.Integer('Replace Number')
    
    
    def set_renew(self):
        if self.expiry_date <= self.bank_guarantees_id.expiry_date:
            raise UserError(_('The new expiration date cannot be less than or equal to the previous expiration date')) 
        else:
            state = 'submitted'
        bank_guarantees_line = self.env['zen.bank.guarantees.line']
        
        #! History Previous BG
        for rec in self.bank_guarantees_id:
            if rec.replace_number:
                bg_number = f"{rec.bg_number} R.{rec.replace_number}"
            else:
                bg_number = f"{rec.bg_number}"
            bank_guarantees_line.sudo().create(
                {
                    'bank_guarantee_number': bg_number,
                    'issue_date': rec.date_of_issuance,
                    'release_date': rec.release_due_date,
                    'bank_expiry_date': rec.expiry_date,
                    'bank_guarantees_id': rec.id,
                    'description' : rec.description,
                    'bg_amount': rec.bg_amount,
                    'state': rec.state
                })
        
        #* New Bank Guarantee
        self.bank_guarantees_id.sudo().write(
            {
                'replace_number': self.replace_number,
                'bg_reference_number': self.bg_reference_number,
                'issuing_bank': self.issuing_bank,
                'type': self.type,
                'date_of_issuance': self.issue_date,
                'release_due_date': self.release_date,
                'bg_amount': rec.bg_amount,
                'state': state,
                'expiry_date': self.expiry_date,
                'description' : self.description,
            })