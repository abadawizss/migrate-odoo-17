# -*- coding: utf-8 -*-
###############################################################################
#
#    Meghsundar Private Limited(<https://www.meghsundar.com>).
#
###############################################################################
from odoo import fields, models


class MasterHSN(models.Model):
    _name = 'master.hsn'
    _description = 'HSN Code'

    name = fields.Char(required=True)
    description = fields.Text()