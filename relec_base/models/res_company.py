# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    ad_code = fields.Char(string="AD Code")


class ResCompany(models.Model):
    _inherit = 'res.company'

    stamp = fields.Image('Stamp', copy=False, attachment=True,
                         help='Stamp will print on reports.',
                         max_width=1024, max_height=1024)
    import_export_code = fields.Char(string="Import-Export Code No")
    iec_no = fields.Char('IEC No')


class Bank(models.Model):
    _inherit = 'res.bank'

    ifsc_code = fields.Char(string="Bank IFSC Code")
