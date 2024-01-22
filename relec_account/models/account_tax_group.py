# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.tax.group"

    desciption = fields.Char(string="Label on Invoice")