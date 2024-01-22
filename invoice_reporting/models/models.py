# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    po_no = fields.Char('PO No')
    po_date = fields.Date('PO Date')
    remark = fields.Text('Remark')
    po_any = fields.Text('Any')


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    # Other Info Fields
    e_way_bill = fields.Char('E-way Bill No')
    station = fields.Char('Station')
    reverse_charge = fields.Char('Reverse Charge')

    # Purchase Order INFO
    po_no = fields.Char('PO No')
    po_date = fields.Date('PO Date')
    remark = fields.Text('Remark')
    others = fields.Text('Others')

    # Transport Fields
    vehicle_number = fields.Char('Vehicle No')
    grr_no = fields.Char('GR/RR No')


# Purchase Order Inherit
class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    Ref_qty_no = fields.Char('Ref QT No:')
    Ref_qty_dt = fields.Date('Ref QT Date:')
    others = fields.Char('Others')
    # po_any = fields.Text('Any')