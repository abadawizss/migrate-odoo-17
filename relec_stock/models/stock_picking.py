# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_shipping_id = fields.Many2one('res.partner', 'Consignee')
    exporter_ref = fields.Char("Exporter's Ref")
    delivery_payment_terms = fields.Text(string="Terms of Delivery & Payment")
    pre_carrier_receipt_place = fields.Char(string="Place of Receipt by Pre Carrier")
    port_loading = fields.Char(string="Port of Loading")
    port_discharge = fields.Char(string="Port of Discharge")
    total_volume = fields.Float(string='Total Volume', store=True, readonly=True)
                                # compute='_compute_total_volume')
#     shipping_gross_weight = fields.Float(string="Shipping Gross Weight")

    @api.depends('package_ids',
                 'package_ids.packaging_id',
                 'package_ids.packaging_id.height',
                 'package_ids.packaging_id.width',
                 'package_ids.packaging_id.length')
    def _compute_total_volume(self):
        for picking in self:
            total_valume = 0
            packages = []
            for package in picking.package_ids:
                if package.packaging_id:
                    if package.id not in packages:
                        packages.append(package.id)
                        tv = (package.packaging_id.height or 1) * (package.packaging_id.width or 1) * (package.packaging_id.length or 1)
                        if tv and tv != 1:
                            total_valume += tv
            if total_valume:
                picking.total_volume = total_valume / 1000000

    @api.model
    def create(self, vals):
        """ Update Consignee default to Delivery Address if not defined."""
        if vals.get('partner_id', False) and not vals.get('partner_shipping_id', False):
            vals['partner_shipping_id'] = vals.get('partner_id')
        return super(StockPicking, self).create(vals)