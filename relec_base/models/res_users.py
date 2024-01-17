# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.users'

    signature_image = fields.Image('Signature Image', copy=False, attachment=True, help='Signature will print on reports.', max_width=1024, max_height=1024)