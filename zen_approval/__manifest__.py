# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Approval Discount And Payment Term',
    'version': '1.0',
    'category': 'Zensoftware/Approval',
    'author': "Zen Software Solutions",
    'summary': 'Zen Approval - v1.1',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'sale_management',
        'hr',
        'base',
        'zen_discount_model',

    ],
    'data': [
        'wizard/zen_mention_reason_views.xml',
        'views/zen_approval.xml',
        'views/zen_configuration_approval_discount.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
