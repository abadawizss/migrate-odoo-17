# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DocumentsFolder(models.Model):
    _inherit = 'documents.document'

    lead_id = fields.Many2one('crm.lead', string='Lead')
