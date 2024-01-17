from odoo import models, fields, api
from dateutil import relativedelta
from datetime import datetime

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    document_count = fields.Integer(compute='_compute_document_count')
    work_space = fields.Many2one('documents.folder', string='Folder',
                                 default=lambda self: self.env['documents.folder'].search([('name', '=', 'Enquiries')], limit=1))
    
    def _compute_document_count(self):
        for lead in self:
            document = self.env['documents.document'].search_count([('lead_id', '=', lead.id), ('sale_order_id', '=', False)])
            lead.document_count = document
    
    def show_relevant_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'view_mode': 'tree',
            'res_model': 'documents.document',
            'domain': [('lead_id', '=', self.id),('sale_order_id', '=', False)],
            'context': "{'create': False}"
        }

    opportunity_sequence = fields.Char(default='/')
    def create_crm_folder(self, res):
        for lead in res:
            x = "x"
            now = datetime.now()
            year_month_str = now.strftime("%Y%m")
            folder_name = f"{year_month_str}"
            
            internal_workspace = self.env['documents.folder'].search([('name', '=', 'Internal')], limit=1)
            sale_workspace = self.env['documents.folder'].search([('name', '=', 'Sale')], limit=1)
            if sale_workspace:
                folder_sale = sale_workspace
            elif not sale_workspace:
                folder_sale_vals = {
                    'name': 'Sale',
                    'parent_folder_id': internal_workspace.id,
                }
                folder_sale = self.env['documents.folder'].sudo().create(folder_sale_vals)
            # # CHECK FOLDER PARENT "ENQUIRES"
            inquiry_folder = self.env['documents.folder'].search([('name', '=', 'Enquiries'), ('parent_folder_id', '=', folder_sale.id)], limit=1)
            if inquiry_folder:
                folder_inquiry = inquiry_folder
            elif not inquiry_folder:
                folder_inquiry_vals = {
                    'name': 'Enquiries',
                    'parent_folder_id': folder_sale.id,
                }
                folder_inquiry = self.env['documents.folder'].sudo().create(folder_inquiry_vals)
            
            existing_folder = self.env['documents.folder'].search([('name', '=', folder_name), ('parent_folder_id', '=', folder_inquiry.id)], limit=1)
            if existing_folder:
                folder_month_year = existing_folder
            else:
                folder_month_year_vals = {
                    'name': folder_name,
                    'parent_folder_id': folder_inquiry.id,
                }
                folder_month_year = self.env['documents.folder'].sudo().create(folder_month_year_vals)
            
            existing_folder_lead = self.env['documents.folder'].search([('name', '=', lead.opportunity_sequence), ('parent_folder_id', '=', folder_inquiry.id)], limit=1)
            if existing_folder_lead:
                folder_lead = existing_folder_lead
            elif not existing_folder_lead:
                folder_lead_vals = {
                    'name': lead.opportunity_sequence,
                    'parent_folder_id': folder_month_year.id,
                }
                folder_lead = self.env['documents.folder'].sudo().create(folder_lead_vals)

        return folder_lead

    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        # Call the function to create a folder and link it to the lead
        if res.opportunity_sequence == '/':
            prefix = 'LEAD'
            res.sudo().write({'opportunity_sequence': f"{prefix}/{res.id}"})
        folder_lead = res.create_crm_folder(res)
        res.sudo().write({'work_space': folder_lead.id})
        return res



class IrAttachmentsLeads(models.Model):
    _inherit = 'ir.attachment'

    
    def _post_add_create(self, **kwargs):
        res = super(IrAttachmentsLeads, self)._post_add_create()
        if self.res_model == 'crm.lead':
            leads = self.env[self.res_model].search([('id','=', self.res_id)])
            for lead in leads:
                attachment_name = f"{lead.opportunity_sequence}"
                existing_folder = self.env['documents.folder'].search([('name', '=', attachment_name)], limit=1)
                if existing_folder:
                    document_vals = {
                        'name': self.name,
                        'datas': self.datas,
                        'folder_id': existing_folder.id,
                        'type': 'binary',
                        'lead_id': lead.id
                    }
                    self.env['documents.document'].sudo().create(document_vals)
        return res