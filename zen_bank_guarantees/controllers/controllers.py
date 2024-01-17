# -*- coding: utf-8 -*-
# from odoo import http


# class ZenBankGuarantees(http.Controller):
#     @http.route('/zen_bank_guarantees/zen_bank_guarantees', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zen_bank_guarantees/zen_bank_guarantees/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('zen_bank_guarantees.listing', {
#             'root': '/zen_bank_guarantees/zen_bank_guarantees',
#             'objects': http.request.env['zen_bank_guarantees.zen_bank_guarantees'].search([]),
#         })

#     @http.route('/zen_bank_guarantees/zen_bank_guarantees/objects/<model("zen_bank_guarantees.zen_bank_guarantees"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zen_bank_guarantees.object', {
#             'object': obj
#         })
