from odoo import models, fields, api
from dateutil import relativedelta
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    document_count = fields.Integer(compute='_compute_document_count')
    work_space = fields.Many2one('documents.folder', string='Folder',
                                 default=lambda self: self.env['documents.folder'].search([('name', '=', 'Enquiries')], limit=1))
    
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['documents.document'].search_count([('sale_order_id','=', rec.id)])
    
    def action_view_document(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'documents.document',
            'view_mode': 'tree',
            'view_id': False,
            'context': "{'create': False}",
            'views': [(self.env.ref('documents.documents_view_list').id, 'tree')],
            'domain': [('sale_order_id','=',self.id)],
            'target': 'current',
        }
        return action
class DocumentsFolder(models.Model):
    _inherit = 'documents.document'

    sale_order_id = fields.Many2one('sale.order', string='Sale Orders')
    

class IrAttachments(models.Model):
    _inherit = 'ir.attachment'

    
    def _post_add_create(self, **kwargs):
        res = super(IrAttachments, self)._post_add_create()
        if self.res_model == 'sale.order':
            sale_order_ids = self.env[self.res_model].search([('id','=', self.res_id)])
            for sale in sale_order_ids:
                if sale.opportunity_id.id:
                    prefix_lead = 'LEAD'
                    sequence_folder = f"{prefix_lead}/{sale.opportunity_id.name}"
                    parent_folder_lead = self.env['documents.folder'].search([('name', '=', sequence_folder)], limit=1)
                    
                    #EXISTING FOLDER LEAD
                    if parent_folder_lead.id:
                        attachment_name = f"{sale.name}"
                        existing_folder = self.env['documents.folder'].search([('name', '=', attachment_name)], limit=1)
                        if existing_folder:
                            print("Folder SO Sudah ada")
                            folder_so = existing_folder
                        else:
                            folder_vals = {
                                'name': attachment_name,
                                'parent_folder_id': parent_folder_lead.folder_id.id,
                            }
                            folder_so = self.env['documents.folder'].create(folder_vals)
                        document_vals = {
                            'name': self.name,
                            'datas': self.datas,
                            'folder_id': folder_so.id,
                            'type': 'binary',
                            'sale_order_id': sale.id,
                            'lead_id': sale.opportunity_id.id
                        }
                        self.env['documents.document'].sudo().create(document_vals)

                    else:
                        #NO EXISTING FOLDER LEAD
                        prefix_lead = 'LEAD'
                        lead_name = f"{prefix_lead}/{sale.opportunity_id.id}"
                        now = sale.opportunity_id.create_date
                        year_month_str = now.strftime("%Y%m")
                        folder_name = f"{year_month_str}"
                        parent_folder = self.env['documents.folder'].search([('name', '=', folder_name)], limit=1)

                        if not parent_folder:
                            parent_folder = self.env['documents.folder'].sudo().create({'name': folder_name})
                        
                        search_folder_lead = self.env['documents.folder'].search([('name', '=', lead_name)])
                        if search_folder_lead:
                            folder_lead = search_folder_lead
                        else:
                            #parent_folder == 202310
                            #lead_name == 'LEAD/0001
                            folder_vals = {
                                'name': lead_name,
                                'parent_folder_id': parent_folder.id,
                            }
                            folder_lead = self.env['documents.folder'].sudo().create(folder_vals)
                        
                       
                        
                        attachment_name = f"{sale.name}"
                        existing_folder = self.env['documents.folder'].search([('name', '=', attachment_name)], limit=1)
                        if existing_folder:
                            print("Folder SO Sudah ada")
                            folder_so = existing_folder
                        else:
                            folder_vals = {
                                'name': attachment_name,
                                'parent_folder_id': folder_lead.id,
                            }
                            folder_so = self.env['documents.folder'].sudo().create(folder_vals)
                        document_vals = {
                            'name': self.name,
                            'datas': self.datas,
                            'folder_id': folder_so.id,
                            'type': 'binary',
                            'sale_order_id': sale.id,
                            'lead_id': sale.opportunity_id.id
                        }
                        self.env['documents.document'].sudo().create(document_vals)
        return res
    
