# -*- coding: utf-8 -*-
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """ Override to pass Transport details to Stock Picking """
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.write({
                    'partner_shipping_id': order.partner_shipping_id.id
                        if order.partner_shipping_id else False,
                    'exporter_ref': order.exporter_ref,
                    'pre_carrier_receipt_place': order.pre_carrier_receipt_place,
                    'port_loading': order.port_loading,
                    'port_discharge': order.port_discharge,
                    'note': order.note,
                    'delivery_payment_terms': self.delivery_payment_terms
                })
        return res