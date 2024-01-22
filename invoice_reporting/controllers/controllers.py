# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceReporting(http.Controller):
#     @http.route('/invoice_reporting/invoice_reporting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_reporting/invoice_reporting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_reporting.listing', {
#             'root': '/invoice_reporting/invoice_reporting',
#             'objects': http.request.env['invoice_reporting.invoice_reporting'].search([]),
#         })

#     @http.route('/invoice_reporting/invoice_reporting/objects/<model("invoice_reporting.invoice_reporting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_reporting.object', {
#             'object': obj
#         })
