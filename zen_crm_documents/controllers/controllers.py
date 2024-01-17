# -*- coding: utf-8 -*-
# from odoo import http


# class ZenCrmDocuments(http.Controller):
#     @http.route('/zen_crm_documents/zen_crm_documents', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zen_crm_documents/zen_crm_documents/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('zen_crm_documents.listing', {
#             'root': '/zen_crm_documents/zen_crm_documents',
#             'objects': http.request.env['zen_crm_documents.zen_crm_documents'].search([]),
#         })

#     @http.route('/zen_crm_documents/zen_crm_documents/objects/<model("zen_crm_documents.zen_crm_documents"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zen_crm_documents.object', {
#             'object': obj
#         })
