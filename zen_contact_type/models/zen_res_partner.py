# -*- coding: utf-8 -*-
from odoo import models, fields


class ZenResPartner(models.Model):
    _inherit = 'res.partner'


    contact_type = fields.Selection([('end_user', 'End User'), ('dealer', 'Dealer')], string='Contact Type', required=True)